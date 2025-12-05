import asyncio
import json
from typing import Optional

from starlette.websockets import WebSocket, WebSocketDisconnect

from src.domain.interfaces.ai_consultation_repository import IAIConsultationRepository
from src.domain.interfaces.doctor_repository import IDoctorRepository
from src.domain.interfaces.speicailization_repository import ISpecializationRepository
from src.domain.interfaces.uow import IUoW
from src.infrastructure.services.jwt_service import JWTService
from src.infrastructure.services.openai_service import OpenAIService


class AIChatHandler:
    def __init__(
            self,
            uow: IUoW,
            consultation_repo: IAIConsultationRepository,
            doctor_repo: IDoctorRepository,
            specialization_repo: ISpecializationRepository,
            openai_service: OpenAIService,
            jwt_service: JWTService,
    ):
        self._uow = uow
        self._consultation_repo = consultation_repo
        self._doctor_repo = doctor_repo
        self._specialization_repo = specialization_repo
        self._openai_service = openai_service
        self._jwt_service = jwt_service

    async def _authenticate(self, websocket: WebSocket) -> Optional[int]:
        """Authenticate user from token query param or first message."""
        token = websocket.query_params.get("token")

        if not token:
            data = await websocket.receive_json()
            token = data.get("token")

        if not token:
            await websocket.send_json({"error": "missing_token"})
            await websocket.close(code=4001)
            return None

        try:
            payload = self._jwt_service.decode_access_token(token)
            user_id = payload.get("sub")
            if not user_id:
                await websocket.send_json({"error": "invalid_token"})
                await websocket.close(code=4001)
                return None
            return int(user_id)
        except Exception:
            await websocket.send_json({"error": "invalid_token"})
            await websocket.close(code=4001)
            return None

    async def handle_chat(self, websocket: WebSocket):
        """Handle AI consultation chat via WebSocket."""
        await websocket.accept()

        user_id = await self._authenticate(websocket)
        if not user_id:
            return

        data = await websocket.receive_json()
        consultation_id = data.get("consultation_id")

        if not consultation_id:
            await websocket.send_json({"error": "missing_consultation_id"})
            await websocket.close(code=1008)
            return

        try:
            consultation_id = int(consultation_id)
        except (TypeError, ValueError):
            await websocket.send_json({"error": "consultation_id_must_be_int"})
            await websocket.close(code=1003)
            return

        consultation = await self._consultation_repo.get_consultation_by_id(consultation_id)
        if not consultation:
            await websocket.send_json({"error": "consultation_not_found"})
            await websocket.close(code=1008)
            return

        if consultation.patient_id != user_id:
            await websocket.send_json({"error": "access_denied"})
            await websocket.close(code=4003)
            return

        await websocket.send_json({
            "type": "connected",
            "consultation_id": consultation_id,
            "status": consultation.status,
        })

        try:
            while True:
                message_data = await websocket.receive_json()
                msg_type = message_data.get("type")

                if msg_type == "message":
                    await self._handle_message(
                        websocket, consultation_id, user_id, message_data.get("content", "")
                    )
                elif msg_type == "complete":
                    await self._handle_complete(websocket, consultation_id, user_id)
                elif msg_type == "history":
                    await self._handle_history(websocket, consultation_id)
                elif msg_type == "ping":
                    await websocket.send_json({"type": "pong"})
                else:
                    await websocket.send_json({"error": "unknown_message_type"})

        except WebSocketDisconnect:
            pass
        except asyncio.CancelledError:
            pass
        finally:
            await websocket.close()

    async def _handle_message(
            self, websocket: WebSocket, consultation_id: int, user_id: int, content: str
    ):
        """Process user message and stream AI response."""
        if not content.strip():
            await websocket.send_json({"error": "empty_message"})
            return

        async with self._uow:
            await self._consultation_repo.add_message(consultation_id, "user", content)

        await websocket.send_json({
            "type": "message_received",
            "role": "user",
            "content": content,
        })

        messages = await self._consultation_repo.get_messages_by_consultation_id(consultation_id)
        chat_messages = [{"role": m.role, "content": m.content} for m in messages]

        await websocket.send_json({"type": "stream_start"})

        full_response = ""
        try:
            async for chunk in self._openai_service.chat_stream(chat_messages):
                full_response += chunk
                await websocket.send_json({
                    "type": "stream_chunk",
                    "content": chunk,
                })
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "message": f"AI service error: {str(e)}",
            })
            return

        async with self._uow:
            await self._consultation_repo.add_message(consultation_id, "assistant", full_response)

        await websocket.send_json({
            "type": "stream_end",
            "role": "assistant",
            "content": full_response,
        })

        if "```json" in full_response:
            recommendation = self._extract_recommendation(full_response)
            if recommendation:
                await websocket.send_json({
                    "type": "recommendation",
                    "data": recommendation,
                })

    async def _handle_complete(self, websocket: WebSocket, consultation_id: int, user_id: int):
        """Complete consultation and provide final analysis."""
        consultation = await self._consultation_repo.get_consultation_by_id(consultation_id)
        messages = await self._consultation_repo.get_messages_by_consultation_id(consultation_id)
        chat_messages = [{"role": m.role, "content": m.content} for m in messages]

        await websocket.send_json({"type": "analyzing"})

        try:
            analysis = await self._openai_service.analyze_symptoms(
                consultation.symptoms_text, chat_messages
            )
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "message": f"Analysis error: {str(e)}",
            })
            return

        specialization = analysis.get("recommended_specialization")
        doctors = []
        if specialization:
            spec = await self._specialization_repo.get_specialization_by_title(specialization)
            if spec:
                doctor_entities = await self._doctor_repo.get_doctors_by_specialization(spec.id)
                doctors = [
                    {
                        "id": d.id,
                        "full_name": d.full_name,
                        "specialization_name": d.specialization_name,
                        "rating": d.rating,
                        "experience_years": d.experience_years,
                    }
                    for d in doctor_entities[:5]
                ]

        from src.use_cases.ai_consultations.dto import UpdateConsultationDTO

        update_dto = UpdateConsultationDTO(
            recommended_specialization=specialization,
            confidence=analysis.get("confidence"),
            ai_response_raw=json.dumps(analysis),
            status="completed",
        )

        async with self._uow:
            await self._consultation_repo.update_consultation(consultation_id, update_dto)

        await websocket.send_json({
            "type": "analysis_complete",
            "analysis": analysis,
            "recommended_doctors": doctors,
        })

    async def _handle_history(self, websocket: WebSocket, consultation_id: int):
        """Send chat history."""
        messages = await self._consultation_repo.get_messages_by_consultation_id(consultation_id)
        history = [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ]
        await websocket.send_json({
            "type": "history",
            "messages": history,
        })

    def _extract_recommendation(self, response: str) -> Optional[dict]:
        """Extract JSON recommendation from AI response."""
        try:
            json_start = response.find("```json") + 7
            json_end = response.find("```", json_start)
            json_str = response[json_start:json_end].strip()
            recommendation = json.loads(json_str)
            if recommendation.get("recommendation"):
                return recommendation
        except (json.JSONDecodeError, KeyError, ValueError):
            pass
        return None


class AIChatStartHandler:
    """Handler for starting new consultations via WebSocket."""

    def __init__(
            self,
            uow: IUoW,
            consultation_repo: IAIConsultationRepository,
            openai_service: OpenAIService,
            jwt_service: JWTService,
    ):
        self._uow = uow
        self._consultation_repo = consultation_repo
        self._openai_service = openai_service
        self._jwt_service = jwt_service

    async def handle_start(self, websocket: WebSocket):
        """Start a new AI consultation."""
        await websocket.accept()

        token = websocket.query_params.get("token")
        if not token:
            await websocket.send_json({"error": "missing_token"})
            await websocket.close(code=4001)
            return

        try:
            payload = self._jwt_service.decode_access_token(token)
            user_id = int(payload.get("sub"))
        except Exception:
            await websocket.send_json({"error": "invalid_token"})
            await websocket.close(code=4001)
            return

        data = await websocket.receive_json()
        symptoms_text = data.get("symptoms_text")

        if not symptoms_text or len(symptoms_text.strip()) < 10:
            await websocket.send_json({"error": "symptoms_text_required_min_10_chars"})
            await websocket.close(code=1008)
            return

        from src.use_cases.ai_consultations.dto import CreateConsultationDTO

        dto = CreateConsultationDTO(
            symptoms_text=symptoms_text,
            patient_id=user_id,
        )

        async with self._uow:
            consultation = await self._consultation_repo.create_consultation(dto)
            await self._consultation_repo.add_message(consultation.id, "user", symptoms_text)

        await websocket.send_json({
            "type": "consultation_created",
            "consultation_id": consultation.id,
        })

        messages = [{"role": "user", "content": symptoms_text}]

        await websocket.send_json({"type": "stream_start"})

        full_response = ""
        try:
            async for chunk in self._openai_service.chat_stream(messages):
                full_response += chunk
                await websocket.send_json({
                    "type": "stream_chunk",
                    "content": chunk,
                })
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "message": f"AI service error: {str(e)}",
            })
            await websocket.close()
            return

        async with self._uow:
            await self._consultation_repo.add_message(consultation.id, "assistant", full_response)

        await websocket.send_json({
            "type": "stream_end",
            "role": "assistant",
            "content": full_response,
        })

        await websocket.close()
