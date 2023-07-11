from sqlalchemy.orm import Mapped
from proxy_app.Database.models.base import Base
from sqlalchemy.orm import mapped_column
from typing import List, Optional

class APIKeyToQuota(Base):
    __tablename__ = "api_key_to_quota"

    api_key: Mapped[str] = mapped_column(primary_key=True)
    rem_quota: Mapped[Optional[float]] = mapped_column()
    req_count: Mapped[Optional[int]] = mapped_column()

    def __repr__(self) -> str:
        return f"(api_key={self.api_key!r}, rem_quota={self.rem_quota!r})"