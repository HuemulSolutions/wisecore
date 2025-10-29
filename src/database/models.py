from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UUID, Boolean, LargeBinary, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
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
    folders = relationship("Folder", back_populates="organization")
    document_types = relationship("DocumentType", back_populates="organization")
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}')>"


class Folder(BaseClass):
    __tablename__ = "folder"
    
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)
    parent_folder_id = Column(UUID(as_uuid=True), ForeignKey("folder.id"), nullable=True)
    
    # Relaciones
    organization = relationship("Organization", back_populates="folders")
    parent_folder = relationship("Folder", remote_side="Folder.id", back_populates="subfolders")
    subfolders = relationship("Folder", back_populates="parent_folder", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="folder", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Folder(id={self.id}, name='{self.name}', parent_id={self.parent_folder_id})>"
    
    @property
    def full_path(self):
        """Retorna la ruta completa de la carpeta"""
        if self.parent_folder:
            return f"{self.parent_folder.full_path}/{self.name}"
        return self.name
    
    @property
    def is_root(self):
        """Indica si es una carpeta raíz (sin padre)"""
        return self.parent_folder_id is None


class DocumentType(BaseClass):
    __tablename__ = "document_type"
    
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=True)
    organization = relationship("Organization", back_populates="document_types")
    
    
    documents = relationship("Document", back_populates="document_type")
    
    def __repr__(self):
        return f"<DocumentType(id={self.id}, name='{self.name}')>"


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
    document_type_id = Column(UUID(as_uuid=True), ForeignKey("document_type.id"), nullable=False)
    folder_id = Column(UUID(as_uuid=True), ForeignKey("folder.id"), nullable=True)
    # template_file = Column(LargeBinary, nullable=True)
    
    organization = relationship("Organization", back_populates="documents")
    template = relationship("Template", back_populates="documents")
    document_type = relationship("DocumentType", back_populates="documents")
    folder = relationship("Folder", back_populates="documents")
    executions = relationship("Execution", back_populates="document", cascade="all, delete-orphan")
    sections = relationship("Section", back_populates="document", cascade="all, delete-orphan")
    docx_template = relationship("DocxTemplate", back_populates="document", cascade="all, delete-orphan")
    

    # Relaciones de dependencias
    dependencies = relationship("Dependency", foreign_keys="Dependency.document_id", back_populates="document", cascade="all, delete-orphan")
    dependants = relationship("Dependency", foreign_keys="Dependency.depends_on_document_id", back_populates="depends_on", cascade="all, delete-orphan")
    contexts = relationship("Context", back_populates="document", cascade="all, delete-orphan")
    
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
    

    
class DocxTemplate(BaseClass):
    __tablename__ = "docx_template"
    
    name = Column(String, nullable=False)
    file_name = Column(String, nullable=False)  # Nombre original del archivo
    mime_type = Column(String, nullable=False, default='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    file_size = Column(Integer, nullable=False)  # Tamaño en bytes
    file_data = Column(LargeBinary, nullable=False)  # El archivo en sí
    document_id = Column(UUID(as_uuid=True), ForeignKey("document.id"), nullable=False)
    
    document = relationship("Document", back_populates="docx_template")
    

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
    chunks = relationship("Chunk", back_populates="section_execution", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SectionExecution(id={self.id}, user_instruction='{self.user_instruction}', output='{self.output}')>"


class Chunk(BaseClass):
    __tablename__ = "chunk"

    content = Column(String, nullable=False)
    embedding = Column(Vector(3072), nullable=False)
    section_execution_id = Column(UUID(as_uuid=True), ForeignKey("section_execution.id"), nullable=False)
    
    section_execution = relationship("SectionExecution", back_populates="chunks")


class CheckpointBlob(Base):
    __tablename__ = "checkpoint_blobs"
    
    thread_id = Column(Text, primary_key=True, nullable=False)
    checkpoint_ns = Column(Text, primary_key=True, nullable=False, default='')
    channel = Column(Text, primary_key=True, nullable=False)
    version = Column(Text, primary_key=True, nullable=False)
    type = Column(Text, nullable=False)
    blob = Column(LargeBinary, nullable=True)
    
    __table_args__ = (
        Index('checkpoint_blobs_thread_id_idx', 'thread_id'),
    )
    
    def __repr__(self):
        return f"<CheckpointBlob(thread_id='{self.thread_id}', checkpoint_ns='{self.checkpoint_ns}', channel='{self.channel}', version='{self.version}')>"


class CheckpointMigrations(Base):
    __tablename__ = "checkpoint_migrations"
    
    v = Column(Integer, primary_key=True, nullable=False)
    
    def __repr__(self):
        return f"<CheckpointMigrations(v={self.v})>"


class CheckpointWrites(Base):
    __tablename__ = "checkpoint_writes"
    
    thread_id = Column(Text, primary_key=True, nullable=False)
    checkpoint_ns = Column(Text, primary_key=True, nullable=False, default='')
    checkpoint_id = Column(Text, primary_key=True, nullable=False)
    task_id = Column(Text, primary_key=True, nullable=False)
    idx = Column(Integer, primary_key=True, nullable=False)
    channel = Column(Text, nullable=False)
    type = Column(Text, nullable=True)
    blob = Column(LargeBinary, nullable=True)
    task_path = Column(Text, nullable=False, default='')
    
    __table_args__ = (
        Index('checkpoint_writes_thread_id_idx', 'thread_id'),
    )
    
    def __repr__(self):
        return f"<CheckpointWrites(thread_id='{self.thread_id}', checkpoint_ns='{self.checkpoint_ns}', checkpoint_id='{self.checkpoint_id}', task_id='{self.task_id}', idx={self.idx})>"


class Checkpoints(Base):
    __tablename__ = "checkpoints"
    
    thread_id = Column(Text, primary_key=True, nullable=False)
    checkpoint_ns = Column(Text, primary_key=True, nullable=False, default='')
    checkpoint_id = Column(Text, primary_key=True, nullable=False)
    parent_checkpoint_id = Column(Text, nullable=True)
    type = Column(Text, nullable=True)
    checkpoint = Column(JSONB, nullable=False)
    metadata_ = Column("metadata", JSONB, nullable=False, default={})  # 👈

    __table_args__ = (
        Index('checkpoints_thread_id_idx', 'thread_id'),
    )

    def __repr__(self):
        return (
            f"<Checkpoints(thread_id='{self.thread_id}', "
            f"checkpoint_ns='{self.checkpoint_ns}', "
            f"checkpoint_id='{self.checkpoint_id}')>"
        )


