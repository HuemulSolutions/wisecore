from src.database.base_model import BaseModel
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Template(BaseModel):
    __tablename__ = "template"
    
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)
    template_sections = relationship("TemplateSection", back_populates="template", cascade="all, delete-orphan")
    organization = relationship("Organization", back_populates="templates")

    
    def __repr__(self):
        return f"<Template(id={self.id}, name='{self.name}')>"