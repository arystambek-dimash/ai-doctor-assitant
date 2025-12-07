from typing import List

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse

from src.domain.entities.users import UserEntity
from src.presentation.api.schemas.requests.ai_consultations import StartConsultationRequest, SendMessageRequest
from src.presentation.api.schemas.responses.ai_consultations import ConsultationResponse, ConsultationAnalysisResponse, \
    ConsultationWithMessagesResponse, ChatMessageResponse
from src.presentation.dependencies import get_current_user, get_ai_consultation_use_case
from src.use_cases.ai_consultations.use_case import AIConsultationUseCase

router = APIRouter(prefix="/ai-consultations", tags=["AI Consultations"])


@router.post(
    "",
    response_model=ConsultationResponse,
    status_code=status.HTTP_201_CREATED
)
async def start_consultation(
        request: StartConsultationRequest,
        current_user: UserEntity = Depends(get_current_user),
        use_case: AIConsultationUseCase = Depends(get_ai_consultation_use_case),
):
    return await use_case.start_consultation(request.symptoms_text, current_user.id)


@router.post(
    "/{consultation_id}/messages",
    response_model=ChatMessageResponse
)
async def send_message(
        consultation_id: int,
        request: SendMessageRequest,
        current_user: UserEntity = Depends(get_current_user),
        use_case: AIConsultationUseCase = Depends(get_ai_consultation_use_case),
):
    return await use_case.send_message(consultation_id, request.content, current_user.id)


@router.post(
    "/{consultation_id}/messages/stream"
)
async def send_message_stream(
        consultation_id: int,
        request: SendMessageRequest,
        current_user: UserEntity = Depends(get_current_user),
        use_cas: AIConsultationUseCase = Depends(get_ai_consultation_use_case),
):
    async def generate():
        async for chunk in use_cas.send_message_stream(
                consultation_id, request.content, current_user.id
        ):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.post(
    "/{consultation_id}/complete",
    response_model=ConsultationAnalysisResponse
)
async def complete_consultation(
        consultation_id: int,
        current_user: UserEntity = Depends(get_current_user),
        use_cas: AIConsultationUseCase = Depends(get_ai_consultation_use_case),
):
    return await use_cas.complete_consultation(consultation_id, current_user.id)


@router.get(
    "/me",
    response_model=List[ConsultationResponse]
)
async def get_my_consultations(
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        current_user: UserEntity = Depends(get_current_user),
        use_cas: AIConsultationUseCase = Depends(get_ai_consultation_use_case),
):
    return await use_cas.get_my_consultations(current_user.id, skip=skip, limit=limit)


@router.get(
    "/{consultation_id}",
    response_model=ConsultationWithMessagesResponse
)
async def get_consultation(
        consultation_id: int,
        current_user: UserEntity = Depends(get_current_user),
        use_cas: AIConsultationUseCase = Depends(get_ai_consultation_use_case),
):
    consultation = await use_cas.get_consultation_by_id(consultation_id, current_user.id)
    messages = await use_cas.get_consultation_messages(consultation_id, current_user.id)
    return {
        "consultation": consultation,
        "messages": messages,
    }


@router.get(
    "/{consultation_id}/messages",
    response_model=List[ChatMessageResponse]
)
async def get_consultation_messages(
        consultation_id: int,
        current_user: UserEntity = Depends(get_current_user),
        use_cas: AIConsultationUseCase = Depends(get_ai_consultation_use_case),
):
    return await use_cas.get_consultation_messages(consultation_id, current_user.id)
