from fastapi import APIRouter, Depends, WebSocket

from src.presentation.dependencies import get_ai_chat_handler, get_ai_chat_start_handler
from src.use_cases.handlers.ai_chat_handler import AIChatHandler, AIChatStartHandler

router = APIRouter(tags=["WebSocket AI Chat"])


@router.websocket("/ws/ai-chat")
async def ai_chat(
        websocket: WebSocket,
        handler: AIChatHandler = Depends(get_ai_chat_handler),
):
    """
    WebSocket endpoint for AI consultation chat.

    Query params:
        - token: JWT token for authentication

    Message types (send):
        - {"type": "message", "content": "your message"}
        - {"type": "complete"} - finish consultation and get analysis
        - {"type": "history"} - get chat history
        - {"type": "ping"} - keep alive

    Message types (receive):
        - {"type": "connected", "consultation_id": int, "status": str}
        - {"type": "message_received", "role": "user", "content": str}
        - {"type": "stream_start"}
        - {"type": "stream_chunk", "content": str}
        - {"type": "stream_end", "role": "assistant", "content": str}
        - {"type": "recommendation", "data": {...}}
        - {"type": "analysis_complete", "analysis": {...}, "recommended_doctors": [...]}
        - {"type": "history", "messages": [...]}
        - {"type": "error", "message": str}
    """
    await handler.handle_chat(websocket)


@router.websocket("/ws/ai-chat/start")
async def ai_chat_start(
        websocket: WebSocket,
        handler: AIChatStartHandler = Depends(get_ai_chat_start_handler),
):
    """
    WebSocket endpoint to start a new AI consultation.

    Query params:
        - token: JWT token for authentication

    First message:
        - {"symptoms_text": "describe your symptoms..."}

    Response:
        - {"type": "consultation_created", "consultation_id": int}
        - Followed by streaming AI response
    """
    await handler.handle_start(websocket)
