"""Repository model for repositories with GitHub App installations."""

from sqlmodel import Field, SQLModel

from app.db.models.base import TimestampMixin


class Repository(SQLModel, TimestampMixin, table=True):
    """Repository model for repos accessible via GitHub App installations."""

    __tablename__ = "repositories"

    id: int | None = Field(default=None, primary_key=True)
    github_repo_id: int = Field(
        unique=True, index=True, description="GitHub repository ID"
    )
    installation_id: int = Field(foreign_key="installations.id", index=True)
    full_name: str = Field(index=True, description="Full repo name (owner/repo)")
    owner: str = Field(description="Repository owner")
    name: str = Field(description="Repository name")
    private: bool = Field(default=False, description="Whether repo is private")
    default_branch: str = Field(default="main", description="Default branch name")
