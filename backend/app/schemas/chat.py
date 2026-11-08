from __future__ import annotations

from typing import Optional
import uuid

from pydantic import BaseModel, ConfigDict


class ChatMessageRequest(BaseModel):
    document_id: uuid.UUID
    sentence_id: Optional[uuid.UUID] = None
    prompt: str


class ChatMessageResponse(BaseModel):
    message_id: uuid.UUID
    session_id: uuid.UUID
    role: str = "ASSISTANT"
    content: str
    active_engine: str
    ai_trial_remaining: int
    balance: int
    ai_chat_allowance_remaining: int

    model_config = ConfigDict(from_attributes=True)


class ParaphraseVariation(BaseModel):
    option_id: int
    style: str
    text: str
    predicted_score: float

    model_config = ConfigDict(from_attributes=True)


class ParaphraseRequest(BaseModel):
    sentence_id: uuid.UUID
    mode: str = "SENTENCE"


class ParaphraseResponse(BaseModel):
    sentence_id: uuid.UUID
    mode: str
    variations: list[ParaphraseVariation]
    active_engine: str

    model_config = ConfigDict(from_attributes=True)


class ApplyParaphraseRequest(BaseModel):
    sentence_id: uuid.UUID
    selected_text: str


class ApplyParaphraseResponse(BaseModel):
    sentence_id: uuid.UUID
    current_text: str
    match_type: str = "RESOLVED_GREEN"
    new_similarity: float
    new_composite_score: float
    is_modified: bool = True

    model_config = ConfigDict(from_attributes=True)
