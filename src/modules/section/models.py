from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database.base_model import BaseModel

class Section(BaseModel):
    __tablename__ = "section"
    
    name = Column(String, nullable=False)
    type = Column(String, nullable=True) # por si se añade una sección tipo imágen
    prompt = Column(String, nullable=True)
    order = Column(Integer, nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("document.id", ondelete="SET NULL"), nullable=False)
    # Ajustar FK para permitir borrar TemplateSection dejando este campo en NULL
    template_section_id = Column(UUID(as_uuid=True), ForeignKey("template_section.id", ondelete="SET NULL"), nullable=True)

    document = relationship("Document", back_populates="sections")
    # Relación inversa hacia TemplateSection
    template_section = relationship("TemplateSection", back_populates="sections")
    
    # Dependencias internas (mismo documento)
    internal_dependencies = relationship("InnerDependency", foreign_keys="InnerDependency.section_id", back_populates="section", cascade="all, delete-orphan")
    internal_dependents = relationship("InnerDependency", foreign_keys="InnerDependency.depends_on_section_id", back_populates="depends_on_section", cascade="all, delete-orphan")
    
    # Dependencias externas (otros documentos)
    external_dependencies = relationship("Dependency", foreign_keys="Dependency.section_id", back_populates="section")
    external_dependents = relationship("Dependency", foreign_keys="Dependency.depends_on_section_id", back_populates="depends_on_section")
    
    section_executions = relationship("SectionExecution", back_populates="section", passive_deletes=True)
    
    @property
    def internal_section_dependencies(self):
        """Secciones del mismo documento de las que depende esta sección"""
        return [dep.depends_on_section for dep in self.internal_dependencies]
    
    @property
    def internal_section_dependents(self):
        """Secciones del mismo documento que dependen de esta sección"""
        return [dep.section for dep in self.internal_dependents]
    
    @property
    def external_section_dependencies(self):
        """Secciones de otros documentos de las que depende esta sección"""
        return [(dep.depends_on.name, dep.depends_on_section.name if dep.depends_on_section else "documento completo") 
                for dep in self.external_dependencies]
    
    
    def __repr__(self):
        return f"<Section(id={self.id}, name='{self.name}', order={self.order})>"




class InnerDependency(BaseModel):
    __tablename__ = "inner_dependency"

    section_id = Column(UUID(as_uuid=True), ForeignKey("section.id"), nullable=False)
    depends_on_section_id = Column(UUID(as_uuid=True), ForeignKey("section.id"), nullable=False)
    
    section = relationship("Section", foreign_keys=[section_id], back_populates="internal_dependencies")
    depends_on_section = relationship("Section", foreign_keys=[depends_on_section_id], back_populates="internal_dependents")