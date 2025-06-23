from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UUID
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from uuid import uuid4
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from enum import Enum


Base = declarative_base()

class BaseClass(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    
class Template(BaseClass):
    __tablename__ = "template"
    
    name = Column(String, nullable=False)
    template_sections = relationship("TemplateSection", back_populates="template")
    
    def __repr__(self):
        return f"<Template(id={self.id}, name='{self.name}')>"
    

class TemplateSection(BaseClass):
    __tablename__ = "template_section"
    
    name = Column(String, nullable=False)
    type = Column(String, nullable=True)
    order = Column(Integer, nullable=False)
    base_prompt = Column(String, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    template_id = Column(UUID(as_uuid=True), ForeignKey("template.id"), nullable=False)
    
    template = relationship("Template", back_populates="template_sections")
    
    def __repr__(self):
        return f"<TemplateSection(id={self.id}, name='{self.name}', order={self.order})>"
    
class Document(BaseClass):
    __tablename__ = "document"
    
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("template.id"), nullable=False)
    template = relationship("Template", back_populates="documents")
    executions = relationship("Execution", back_populates="document")
    
    def __repr__(self):
        return f"<Document(id={self.id}, name='{self.name}', template_id={self.template_id})>"
    
    
class Dependency(BaseClass):
    __tablename__ = "dependency"
    
    depends_on = Column(String, nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("document.id"), nullable=False)
    
    
class Section(BaseClass):
    __tablename__ = "section"
    
    name = Column(String, nullable=False)
    type = Column(String, nullable=True) # por si se añade una sección tipo imágen
    base_prompt = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("document.id"), nullable=False)
    template_section_id = Column(UUID(as_uuid=True), ForeignKey("template_section.id"), nullable=True)

    document = relationship("Document", back_populates="sections")
    
    def __repr__(self):
        return f"<Section(id={self.id}, name='{self.name}', order={self.order})>"
    
class Restriction(BaseClass):
    __tablename__ = "restriction"
    
    name = Column(String, nullable=False)
    prompt = Column(String, nullable=False)
    section_id = Column(UUID(as_uuid=True), ForeignKey("section.id"), nullable=False)
    
    section = relationship("Section", back_populates="restrictions")
    evaluations = relationship("Evaluation", back_populates="restriction")
    
    def __repr__(self):
        return f"<Restriction(id={self.id}, name='{self.name}', section_id={self.section_id})>"
    
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
    section_id = Column(UUID(as_uuid=True), ForeignKey("section.id"), nullable=False)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("execution.id"), nullable=False)
    
    section = relationship("Section", back_populates="section_executions")
    execution = relationship("Execution", back_populates="sections")
    
    def __repr__(self):
        return f"<SectionExecution(id={self.id}, user_instruction='{self.user_instruction}', output='{self.output}')>"
    



