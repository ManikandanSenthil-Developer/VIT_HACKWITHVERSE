from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.services.copilot.copilot_service import copilot_service

router = APIRouter()


class CopilotChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User query or instruction")
    conversation_id: Optional[int] = Field(None, description="Optional conversation ID for context continuity")
    language: Optional[str] = Field(None, description="Preferred language code ('en', 'ta', 'hi')")


class CopilotChatResponse(BaseModel):
    conversation_id: int
    message_id: int
    intent: str
    language: Optional[str] = "en"
    summary: str
    key_findings: List[str]
    evidence: List[str]
    risks: List[str]
    counterarguments: List[str]
    follow_ups: List[str]
    tool_calls: List[str]
    citations: List[str]


@router.post("/chat", response_model=CopilotChatResponse)
async def copilot_chat(
    req: CopilotChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Interact with the Investor Copilot.
    Invokes registered analytical tools, enforces decision-support boundaries,
    and returns grounded, evidence-backed financial intelligence.
    """
    try:
        return await copilot_service.chat(
            db=db,
            user_id=current_user.id,
            message=req.message,
            conversation_id=req.conversation_id,
            language=req.language,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Copilot reasoning execution error: {str(e)}",
        )


@router.get("/conversations")
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[Dict[str, Any]]:
    """List all copilot conversations for the authenticated user."""
    return copilot_service.list_conversations(db=db, user_id=current_user.id)


@router.get("/conversations/{conversation_id}")
def get_conversation_thread(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[Dict[str, Any]]:
    """Retrieve full message history for a specific conversation thread."""
    try:
        return copilot_service.get_conversation_messages(
            db=db,
            user_id=current_user.id,
            conversation_id=conversation_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, str]:
    """Delete a conversation thread and its associated message history."""
    deleted = copilot_service.delete_conversation(
        db=db,
        user_id=current_user.id,
        conversation_id=conversation_id,
    )
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")
    return {"status": "success", "message": "Conversation deleted successfully."}
