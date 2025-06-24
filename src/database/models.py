from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UUID, Boolean
from pgvector.sqlalchemy import Vector
from uuid import uuid4
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship, declarative_base, foreign, remote
from sqlalchemy.sql import func
from enum import Enum


Base = declarative_base()

class BaseClass(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())


class Dependency(BaseClass):
    __tablename__ = "dependency"
    
    document_id = Column(UUID(as_uuid=True), ForeignKey("document.id"), nullable=False)
    section_id = Column(UUID(as_uuid=True), ForeignKey("section.id"), nullable=True)
    depends_on_document_id = Column(UUID(as_uuid=True), ForeignKey("document.id"), nullable=False)
    depends_on_section_id = Column(UUID(as_uuid=True), ForeignKey("section.id"), nullable=True)
    
    document = relationship("Document", foreign_keys=[document_id], back_populates="dependencies_relations")
    depends_on = relationship("Document", foreign_keys=[depends_on_document_id], back_populates="dependants_relations")
    section = relationship("Section", foreign_keys=[section_id], back_populates="external_dependencies")
    depends_on_section = relationship("Section", foreign_keys=[depends_on_section_id], back_populates="external_dependents")
    
    def __repr__(self):
        return f"<Dependency(document_id={self.document_id}, depends_on_id={self.depends_on})>"


class InnerDependency(BaseClass):
    __tablename__ = "inner_dependency"

    section_id = Column(UUID(as_uuid=True), ForeignKey("section.id"), nullable=False)
    depends_on_section_id = Column(UUID(as_uuid=True), ForeignKey("section.id"), nullable=False)
    
    section = relationship("Section", foreign_keys=[section_id], back_populates="internal_dependencies")
    depends_on_section = relationship("Section", foreign_keys=[depends_on_section_id], back_populates="internal_dependents")


class Template(BaseClass):
    __tablename__ = "template"
    
    name = Column(String, nullable=False)
    template_sections = relationship("TemplateSection", back_populates="template")
    documents = relationship("Document", back_populates="template")
    
    def __repr__(self):
        return f"<Template(id={self.id}, name='{self.name}')>"
    

class TemplateSection(BaseClass):
    __tablename__ = "template_section"
    
    name = Column(String, nullable=False)
    type = Column(String, nullable=True)
    order = Column(Integer, nullable=False)
    prompt = Column(String, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    template_id = Column(UUID(as_uuid=True), ForeignKey("template.id"), nullable=False)
    
    template = relationship("Template", back_populates="template_sections")
    # Estas relaciones son para dependencias en plantillas
    dependencies = relationship("InnerDependency", foreign_keys="InnerDependency.section_id", back_populates="section")
    dependents = relationship("InnerDependency", foreign_keys="InnerDependency.depends_on_section_id", back_populates="depends_on_section")
    
    def __repr__(self):
        return f"<TemplateSection(id={self.id}, name='{self.name}', order={self.order})>"
    

    
class Document(BaseClass):
    __tablename__ = "document"
    
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("template.id"), nullable=True)
    
    template = relationship("Template", back_populates="documents")
    executions = relationship("Execution", back_populates="document")
    sections = relationship("Section", back_populates="document")

    # Renombrar para evitar confusión con las properties
    dependencies_relations = relationship("Dependency", foreign_keys="Dependency.document_id", back_populates="document")
    dependants_relations = relationship("Dependency", foreign_keys="Dependency.depends_on_document_id", back_populates="depends_on")
    
    @property
    def document_dependencies(self):
        """Documentos de los que depende este documento (solo dependencias a nivel documento)"""
        return [dep.depends_on for dep in self.dependencies_relations 
                if dep.section_id is None and dep.depends_on_section_id is None]
    
    @property
    def document_dependents(self):
        """Documentos que dependen de este documento"""
        return [dep.document for dep in self.dependants_relations
                if dep.section_id is None and dep.depends_on_section_id is None]
    
    @property
    def cross_section_dependencies(self):
        """Dependencias específicas entre secciones de diferentes documentos"""
        return [dep for dep in self.dependencies_relations 
                if dep.section_id is not None or dep.depends_on_section_id is not None]
    
    def __repr__(self):
        return f"<Document(id={self.id}, name='{self.name}', template_id={self.template_id})>"
    
    
class Section(BaseClass):
    __tablename__ = "section"
    
    name = Column(String, nullable=False)
    type = Column(String, nullable=True) # por si se añade una sección tipo imágen
    prompt = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("document.id"), nullable=False)
    template_section_id = Column(UUID(as_uuid=True), ForeignKey("template_section.id"), nullable=True)
    context_dependency_id = Column(UUID(as_uuid=True), ForeignKey("dependency.id"), nullable=True)

    document = relationship("Document", back_populates="sections")
    
    # Dependencias internas (mismo documento)
    internal_dependencies = relationship("InnerDependency", foreign_keys="InnerDependency.section_id", back_populates="section")
    internal_dependents = relationship("InnerDependency", foreign_keys="InnerDependency.depends_on_section_id", back_populates="depends_on_section")
    
    # Dependencias externas (otros documentos)
    external_dependencies = relationship("Dependency", foreign_keys="Dependency.section_id", back_populates="section")
    external_dependents = relationship("Dependency", foreign_keys="Dependency.depends_on_section_id", back_populates="depends_on_section")
    
    section_executions = relationship("SectionExecution", back_populates="section")
    chunks = relationship("Chunk", back_populates="section")
    
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
    
class Status(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    APPROVED = "approved"    

class Execution(BaseClass):
    __tablename__ = "execution"
    
    user_instruction = Column(String, nullable=True)
    status = Column(SAEnum(Status, name="status_enum"), nullable=False)
    status_message = Column(String, nullable=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("document.id"), nullable=False)
    
    document = relationship("Document", back_populates="executions")
    sections_executions = relationship("SectionExecution", back_populates="execution")
    
    def __repr__(self):
        return f"<Execution(id={self.id}, status={self.status.value}, document_id={self.document.name})>"
    

class SectionExecution(BaseClass):
    __tablename__ = "section_execution"

    user_instruction = Column(String, nullable=True)
    output = Column(String, nullable=True)
    custom_output = Column(String, nullable=True)
    is_locked = Column(Boolean, default=False, nullable=False)
    section_id = Column(UUID(as_uuid=True), ForeignKey("section.id"), nullable=False)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("execution.id"), nullable=False)
    
    section = relationship("Section", back_populates="section_executions")
    execution = relationship("Execution", back_populates="sections_executions")
    
    def __repr__(self):
        return f"<SectionExecution(id={self.id}, user_instruction='{self.user_instruction}', output='{self.output}')>"


class Chunk(BaseClass):
    __tablename__ = "chunk"

    content = Column(String, nullable=False)
    embedding = Column(Vector(3072), nullable=False)
    section_id = Column(UUID(as_uuid=True), ForeignKey("section.id"), nullable=False)
    
    section = relationship("Section", back_populates="chunks")



