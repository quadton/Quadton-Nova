"""Declarative base and the schema metadata table."""

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Bump when tables change. Until migrations exist, a mismatch is refused rather than guessed at.
SCHEMA_VERSION = 1


class Base(DeclarativeBase):
    """Declarative base for all NOVA tables. Import models before calling init_db."""


class SchemaInfo(Base):
    """Key/value table holding database metadata, currently the schema version."""

    __tablename__ = "schema_info"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(String(255))
