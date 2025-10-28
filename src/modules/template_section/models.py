from src.database.base_model import BaseModel
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
# from src.modules.templates.models import Template

class TemplateSection(BaseModel):
    __tablename__ = "template_section"
    
    name = Column(String, nullable=False)
    type = Column(String, nullable=True)
    order = Column(Integer, nullable=False)
    prompt = Column(String, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    template_id = Column(UUID(as_uuid=True), ForeignKey("template.id"), nullable=False)
    
    template = relationship("Template", back_populates="template_sections")
    
    # Dependencias internas entre secciones de la plantilla
    internal_dependencies = relationship("TemplateSectionDependency", foreign_keys="TemplateSectionDependency.template_section_id",
                                         back_populates="template_section", cascade="all, delete-orphan")
    internal_dependents = relationship("TemplateSectionDependency", foreign_keys="TemplateSectionDependency.depends_on_template_section_id", 
                                       back_populates="depends_on_template_section", cascade="all, delete-orphan")
    
    # Hacer que las secciones que referencian a esta TemplateSection se desvinculen (SET NULL) al borrar
    # sections = relationship("Section", back_populates="template_section", passive_deletes=True)
    
    def __repr__(self):
        return f"<TemplateSection(id={self.id}, name='{self.name}', order={self.order})>"

class TemplateSectionDependency(BaseModel):
    __tablename__ = "template_section_dependency"

    template_section_id = Column(UUID(as_uuid=True), ForeignKey("template_section.id"), nullable=False)
    depends_on_template_section_id = Column(UUID(as_uuid=True), ForeignKey("template_section.id"), nullable=False)
    
    template_section = relationship("TemplateSection", foreign_keys=[template_section_id], 
                                    back_populates="internal_dependencies")
    depends_on_template_section = relationship("TemplateSection", foreign_keys=[depends_on_template_section_id], 
                                               back_populates="internal_dependents")

    def __repr__(self):
        return f"<TemplateSectionDependency(template_section_id={self.template_section_id}, depends_on={self.depends_on_template_section_id})>"
