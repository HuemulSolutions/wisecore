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
    

class Organization(BaseClass):
    __tablename__ = "organization"
    
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    documents = relationship("Document", back_populates="organization")
    templates = relationship("Template", back_populates="organization")
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}')>"


class Dependency(BaseClass):
    __tablename__ = "dependency"
    
    document_id = Column(UUID(as_uuid=True), ForeignKey("document.id"), nullable=False)
    section_id = Column(UUID(as_uuid=True), ForeignKey("section.id"), nullable=True)
    depends_on_document_id = Column(UUID(as_uuid=True), ForeignKey("document.id"), nullable=False)
    depends_on_section_id = Column(UUID(as_uuid=True), ForeignKey("section.id"), nullable=True)
    
    document = relationship("Document", foreign_keys=[document_id], back_populates="dependencies")
    depends_on = relationship("Document", foreign_keys=[depends_on_document_id], back_populates="dependants")
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
    description = Column(String, nullable=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)
    template_sections = relationship("TemplateSection", back_populates="template", cascade="all, delete-orphan")
    organization = relationship("Organization", back_populates="templates")
    documents = relationship("Document", back_populates="template")
    
    def __repr__(self):
        return f"<Template(id={self.id}, name='{self.name}')>"
    

class TemplateSectionDependency(BaseClass):
    __tablename__ = "template_section_dependency"

    template_section_id = Column(UUID(as_uuid=True), ForeignKey("template_section.id"), nullable=False)
    depends_on_template_section_id = Column(UUID(as_uuid=True), ForeignKey("template_section.id"), nullable=False)
    
    template_section = relationship("TemplateSection", foreign_keys=[template_section_id], 
                                    back_populates="internal_dependencies")
    depends_on_template_section = relationship("TemplateSection", foreign_keys=[depends_on_template_section_id], 
                                               back_populates="internal_dependents")

    def __repr__(self):
        return f"<TemplateSectionDependency(template_section_id={self.template_section_id}, depends_on={self.depends_on_template_section_id})>"


class TemplateSection(BaseClass):
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
    sections = relationship("Section", back_populates="template_section", passive_deletes=True)
    
    def __repr__(self):
        return f"<TemplateSection(id={self.id}, name='{self.name}', order={self.order})>"
    

    
class Document(BaseClass):
    __tablename__ = "document"
    
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("template.id"), nullable=True)
    
    organization = relationship("Organization", back_populates="documents")
    template = relationship("Template", back_populates="documents")
    executions = relationship("Execution", back_populates="document")
    sections = relationship("Section", back_populates="document", cascade="all, delete-orphan")

    # Relaciones de dependencias
    dependencies = relationship("Dependency", foreign_keys="Dependency.document_id", back_populates="document", cascade="all, delete-orphan")
    dependants = relationship("Dependency", foreign_keys="Dependency.depends_on_document_id", back_populates="depends_on", cascade="all, delete-orphan")
    contexts = relationship("Context", back_populates="document")
    
    def __repr__(self):
        return f"<Document(id={self.id}, name='{self.name}', template_id={self.template_id})>"
    
    
class Context(BaseClass):
    __tablename__ = "context"
    
    name = Column(String, nullable=False)
    content = Column(String, nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("document.id"), nullable=False)
    document = relationship("Document", back_populates="contexts")
    
    def __repr__(self):
        return f"<Context(id={self.id}, name='{self.name}', document_id={self.document_id})>"
    
    
class Section(BaseClass):
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
    
    
class LLM(BaseClass):
    __tablename__ = "llm"
    
    name = Column(String, nullable=False)
    executions = relationship("Execution", back_populates="model")
    
    def __repr__(self):
        return f"<LLM(id={self.id}, name='{self.name}')>"
    
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
    model_id = Column(UUID(as_uuid=True), ForeignKey("llm.id"), nullable=True)
    
    document = relationship("Document", back_populates="executions")
    model = relationship("LLM", back_populates="executions")
    sections_executions = relationship("SectionExecution", back_populates="execution", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Execution(id={self.id}, status={self.status.value}, document_id={self.document.name})>"
    

class SectionExecution(BaseClass):
    __tablename__ = "section_execution"

    name = Column(String, nullable=True) # Cambiar después de migración
    user_instruction = Column(String, nullable=True)
    prompt = Column(String, nullable=True)
    order = Column(Integer, nullable=False)
    output = Column(String, nullable=True)
    custom_output = Column(String, nullable=True)
    is_locked = Column(Boolean, default=False, nullable=False)
    section_id = Column(UUID(as_uuid=True), ForeignKey("section.id", ondelete="SET NULL"), nullable=True)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("execution.id"), nullable=False)
    
    
    section = relationship("Section", back_populates="section_executions")
    execution = relationship("Execution", back_populates="sections_executions")
    chunks = relationship("Chunk", back_populates="section_execution")
    
    def __repr__(self):
        return f"<SectionExecution(id={self.id}, user_instruction='{self.user_instruction}', output='{self.output}')>"


class Chunk(BaseClass):
    __tablename__ = "chunk"

    content = Column(String, nullable=False)
    embedding = Column(Vector(3072), nullable=False)
    section_execution_id = Column(UUID(as_uuid=True), ForeignKey("section_execution.id"), nullable=False)
    
    section_execution = relationship("SectionExecution", back_populates="chunks")



