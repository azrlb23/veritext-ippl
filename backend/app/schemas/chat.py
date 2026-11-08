from __future__ import annotations

from typing import Optional
import uuid

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChatMessageRequest(BaseModel):
    document_id: Optional[uuid.UUID] = None
    document_ids: list[uuid.UUID] = Field(default_factory=list, max_length=3)
    session_id: Optional[uuid.UUID] = None
    sentence_id: Optional[uuid.UUID] = None
    prompt: str = Field(min_length=1, max_length=4000)

    def all_document_ids(self) -> list[uuid.UUID]:
        merged = list(self.document_ids)
        if self.document_id and self.document_id not in merged:
            merged.append(self.document_id)
        return merged[:3]


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


class ChatSessionItem(BaseModel):
    id: uuid.UUID
    title: str
    document_ids: list[uuid.UUID]
    last_message: Optional[str] = None
    message_count: int = 0
    updated_at: datetime


class ChatHistoryItem(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    mode: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
