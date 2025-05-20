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
    documents = relationship("Document", back_populates="template")
    sections = relationship("Section", back_populates="template")
    
    def __repr__(self):
        return f"<Template(id={self.id}, name='{self.name}')>"
    
    
class Section(BaseClass):
    __tablename__ = "section"
    
    name = Column(String, nullable=False)
    type = Column(String, nullable=True) # por si se añade una sección tipo imágen
    init_prompt = Column(String, nullable=False)
    final_prompt = Column(String, nullable=True)
    order = Column(Integer, nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("template.id"), nullable=False)
    
    template = relationship("Template", back_populates="sections")
    dependencies = relationship(
        "Dependency",
        primaryjoin="Section.id == Dependency.section_id",
        back_populates="section"
    )
    restrictions = relationship("Restriction", back_populates="section")
    executions = relationship("SectionExecution", back_populates="section")
    
    def __repr__(self):
        dep_str = ', '.join([f"{d.type.value}:{d.depends_on}" for d in self.dependencies])
        return f"<Section(id={self.id}, name='{self.name}', order={self.order}, dependencies=[{dep_str}])>"
    
class DependencyType(Enum):
    SECTION = "section"
    KNOWLEDGE = "knowledge"
    
    
class Dependency(BaseClass):
    __tablename__ = "dependency"
    
    section_id = Column(UUID(as_uuid=True), ForeignKey("section.id"), nullable=False)
    type = Column(SAEnum(DependencyType, name="dependency_type_enum"), nullable=False)
    depends_on = Column(String, nullable=False)
    
    section = relationship("Section", foreign_keys=[section_id], back_populates="dependencies")
    
    def __repr__(self):
        return f"<Dependency(id={self.id}, section_id={self.section_id}, type={self.type.value}, depends_on='{self.depends_on}')>"
    
    
class Restriction(BaseClass):
    __tablename__ = "restriction"
    
    name = Column(String, nullable=False)
    prompt = Column(String, nullable=False)
    section_id = Column(UUID(as_uuid=True), ForeignKey("section.id"), nullable=False)
    
    section = relationship("Section", back_populates="restrictions")
    evaluations = relationship("Evaluation", back_populates="restriction")
    
    def __repr__(self):
        return f"<Restriction(id={self.id}, name='{self.name}', section_id={self.section_id})>"
    

class Document(BaseClass):
    __tablename__ = "document"
    
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("template.id"), nullable=False)
    template = relationship("Template", back_populates="documents")
    executions = relationship("Execution", back_populates="document")
    
    def __repr__(self):
        return f"<Document(id={self.id}, name='{self.name}', template_id={self.template_id})>"
    
class Status(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"    

class Execution(BaseClass):
    __tablename__ = "execution"
    
    status = Column(SAEnum(Status, name="status_enum"), nullable=False)
    status_message = Column(String, nullable=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("document.id"), nullable=False)
    
    document = relationship("Document", back_populates="executions")
    sections = relationship("SectionExecution", back_populates="execution")
    
    def __repr__(self):
        return f"<Execution(id={self.id}, status={self.status.value}, document_id={self.document_id})>"
    

class SectionExecution(BaseClass):
    __tablename__ = "section_execution"

    output = Column(String, nullable=True)
    section_id = Column(UUID(as_uuid=True), ForeignKey("section.id"), nullable=False)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("execution.id"), nullable=False)
    
    section = relationship("Section", back_populates="executions")
    execution = relationship("Execution", back_populates="sections")
    evaluations = relationship("Evaluation", back_populates="section_execution")
    knowledge_base = relationship("KnowledgeBase", back_populates="section_execution")
    
    def __repr__(self):
        return f"<SectionExecution(id={self.id}, section_id={self.section_id}, execution_id={self.execution_id})>"
    
class Evaluation(BaseClass):
    __tablename__ = "evaluation"
    
    result = Column(String, nullable=False)
    justification = Column(String, nullable=True)
    section_execution_id = Column(UUID(as_uuid=True), ForeignKey("section_execution.id"), nullable=False)
    restriction_id = Column(UUID(as_uuid=True), ForeignKey("restriction.id"), nullable=False)
    
    section_execution = relationship("SectionExecution", back_populates="evaluations")
    restriction = relationship("Restriction", back_populates="evaluations")
    
    def __repr__(self):
        return f"<Evaluation(id={self.id}, result='{self.result}', section_execution_id={self.section_execution_id}, restriction_id={self.restriction_id})>"
    
class KnowledgeBase(BaseClass):
    __tablename__ = "knowledge_base"
    
    name = Column(String, nullable=False)
    content = Column(String, nullable=False)
    section_execution_id = Column(UUID(as_uuid=True), ForeignKey("section_execution.id"), nullable=True)
    
    section_execution = relationship("SectionExecution", back_populates="knowledge_base")
    
    def __repr__(self):
        return f"<KnowledgeBase(id={self.id}, name='{self.name}', section_execution_id={self.section_execution_id})>"





