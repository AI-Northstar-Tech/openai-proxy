from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, column_property
from typing import List, Optional
from typing import Any
from proxy_app.Database.models.apiKeyToQuota import APIKeyToQuota, Base
from sqlalchemy import Column, Integer

class OpenAIRequestResponse(Base):
    __tablename__ = "openai_request_response"

    req_id: Mapped[str] = mapped_column(primary_key=True)
    api_key: Mapped[str] = mapped_column(ForeignKey("api_key_to_quota.api_key"))
    req_data: Mapped[Optional[dict[str, Any]]] = mapped_column()
    response: Mapped[Optional[dict[str, Any]]] = mapped_column()

    def __repr__(self) -> str:
        return f"(api_key={self.api_key!r}, req_data={self.req_data!r}, response={self.response!r})"