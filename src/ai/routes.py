from fastapi import APIRouter, Depends
from src.auth.dependecies import get_current_user
from src.web.note import read_note
from src.ai.services import summarize_notes,grammar_check
from src.core.sliding_rate_limiter import SlidingWindowRateLimiter


router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/notes/{note_id}/summarize",dependencies=[Depends(SlidingWindowRateLimiter.from_config("AI_SUMMARIZE"))])
async def summarize(
    note_id: str,
    current_user: dict = Depends(get_current_user) # Add this
):
    # Pass current_user explicitly
    note = await read_note(note_id, current_user=current_user)
    result = await summarize_notes(note["content"])
    return result

@router.post("/notes/{note_id}/grammar_check",dependencies=[Depends(SlidingWindowRateLimiter.from_config("AI_GRAMMAR"))])
async def check_grammar(
    note_id: str,
    current_user: dict = Depends(get_current_user) # Add this
):
    # Pass current_user explicitly
    note = await read_note(note_id, current_user=current_user)
    result = await grammar_check(note["content"])
    return result
