import json
from typing import AsyncGenerator

from src.domain.entities.ai_consultations import AIConsultationEntity, ChatMessageEntity
from src.domain.errors import NotFoundException, ForbiddenException
from src.domain.interfaces.ai_consultation_repository import IAIConsultationRepository
from src.domain.interfaces.doctor_repository import IDoctorRepository
from src.domain.interfaces.speicailization_repository import ISpecializationRepository
from src.domain.interfaces.uow import IUoW
from src.infrastructure.services.openai_service import OpenAIService
from src.use_cases.ai_consultations.dto import CreateConsultationDTO, UpdateConsultationDTO


class AIConsultationUseCase:
    def __init__(
            self,
            uow: IUoW,
            consultation_repository: IAIConsultationRepository,
            doctor_repository: IDoctorRepository,
            specialization_repository: ISpecializationRepository,
            openai_service: OpenAIService,
    ):
        self._uow = uow
        self._consultation_repo = consultation_repository
        self._doctor_repo = doctor_repository
        self._specialization_repo = specialization_repository
        self._openai_service = openai_service

    async def start_consultation(
            self, symptoms_text: str, user_id: int
    ) -> AIConsultationEntity:
        dto = CreateConsultationDTO(
            symptoms_text=symptoms_text,
            patient_id=user_id,
        )

        async with self._uow:
            consultation = await self._consultation_repo.create_consultation(dto)
            await self._consultation_repo.add_message(
                consultation.id, "user", symptoms_text
            )

        return consultation

    async def send_message_stream(
            self, consultation_id: int, content: str, user_id: int
    ) -> AsyncGenerator[str, None]:
        consultation = await self._consultation_repo.get_consultation_by_id(consultation_id)
        if not consultation:
            raise NotFoundException("Consultation not found")

        if consultation.patient_id != user_id:
            raise ForbiddenException("Access denied")

        async with self._uow:
            await self._consultation_repo.add_message(consultation_id, "user", content)

        messages = await self._consultation_repo.get_messages_by_consultation_id(consultation_id)
        chat_messages = [{"role": m.role, "content": m.content} for m in messages]

        full_response = ""
        async for chunk in self._openai_service.chat_stream(chat_messages):
            full_response += chunk
            yield chunk

        async with self._uow:
            await self._consultation_repo.add_message(consultation_id, "assistant", full_response)

        if "```json" in full_response:
            await self._process_recommendation(consultation_id, full_response)

    async def send_message(
            self, consultation_id: int, content: str, user_id: int
    ) -> ChatMessageEntity:
        consultation = await self._consultation_repo.get_consultation_by_id(consultation_id)
        if not consultation:
            raise NotFoundException("Consultation not found")

        if consultation.patient_id != user_id:
            raise ForbiddenException("Access denied")

        async with self._uow:
            await self._consultation_repo.add_message(consultation_id, "user", content)

        messages = await self._consultation_repo.get_messages_by_consultation_id(consultation_id)
        chat_messages = [{"role": m.role, "content": m.content} for m in messages]

        response = await self._openai_service.chat(chat_messages)

        async with self._uow:
            message = await self._consultation_repo.add_message(
                consultation_id, "assistant", response
            )

        if "```json" in response:
            await self._process_recommendation(consultation_id, response)

        return message

    async def _process_recommendation(self, consultation_id: int, response: str) -> None:
        try:
            json_start = response.find("```json") + 7
            json_end = response.find("```", json_start)
            json_str = response[json_start:json_end].strip()
            recommendation = json.loads(json_str)

            if recommendation.get("recommendation"):
                update_dto = UpdateConsultationDTO(
                    recommended_specialization=recommendation.get("specialization"),
                    confidence=recommendation.get("confidence"),
                    ai_response_raw=json_str,
                    status="completed",
                )
                async with self._uow:
                    await self._consultation_repo.update_consultation(consultation_id, update_dto)
        except (json.JSONDecodeError, KeyError):
            pass

    async def complete_consultation(
            self, consultation_id: int, user_id: int
    ) -> dict:
        consultation = await self._consultation_repo.get_consultation_by_id(consultation_id)
        if not consultation:
            raise NotFoundException("Consultation not found")

        if consultation.patient_id != user_id:
            raise ForbiddenException("Access denied")

        messages = await self._consultation_repo.get_messages_by_consultation_id(consultation_id)
        chat_messages = [{"role": m.role, "content": m.content} for m in messages]

        analysis = await self._openai_service.analyze_symptoms(
            consultation.symptoms_text, chat_messages
        )

        specialization = analysis.get("recommended_specialization")
        doctors = []
        if specialization:
            spec = await self._specialization_repo.get_specialization_by_title(specialization)
            if spec:
                doctors = await self._doctor_repo.get_doctors_by_specialization(spec.id)

        update_dto = UpdateConsultationDTO(
            recommended_specialization=specialization,
            confidence=analysis.get("confidence"),
            ai_response_raw=json.dumps(analysis),
            status="completed",
        )

        async with self._uow:
            await self._consultation_repo.update_consultation(consultation_id, update_dto)

        return {
            "analysis": analysis,
            "recommended_doctors": doctors[:5],
        }

    async def get_consultation_by_id(
            self, consultation_id: int, user_id: int
    ) -> AIConsultationEntity:
        consultation = await self._consultation_repo.get_consultation_by_id(consultation_id)
        if not consultation:
            raise NotFoundException("Consultation not found")

        if consultation.patient_id != user_id:
            raise ForbiddenException("Access denied")

        return consultation

    async def get_consultation_messages(
            self, consultation_id: int, user_id: int
    ) -> list[ChatMessageEntity]:
        consultation = await self._consultation_repo.get_consultation_by_id(consultation_id)
        if not consultation:
            raise NotFoundException("Consultation not found")

        if consultation.patient_id != user_id:
            raise ForbiddenException("Access denied")

        return await self._consultation_repo.get_messages_by_consultation_id(consultation_id)

    async def get_my_consultations(
            self, user_id: int, skip: int = 0, limit: int = 20
    ) -> list[AIConsultationEntity]:
        return await self._consultation_repo.get_consultations_by_patient_id(
            user_id, skip=skip, limit=limit
        )
