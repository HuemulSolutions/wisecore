from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from enum import Enum


Base = declarative_base()

class BaseClass(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    
class Template(BaseClass):
    __tablename__ = "template"
    
    name = Column(String, nullable=False)
    documents = relationship("Document", back_populates="template")
    sections = relationship("Section", back_populates="template")
    
    
class Section(BaseClass):
    __tablename__ = "section"
    
    name = Column(String, nullable=False)
    type = Column(String, nullable=True)
    init_prompt = Column(String, nullable=False)
    final_prompt = Column(String, nullable=True)
    order = Column(Integer, nullable=False)
    template_id = Column(Integer, ForeignKey("template.id"), nullable=False)
    
    template = relationship("Template", back_populates="sections")
    dependencies = relationship(
        "Dependency",
        primaryjoin="Section.id == Dependency.section_id",
        back_populates="section"
    )
    restrictions = relationship("Restriction", back_populates="section")
    executions = relationship("SectionExecution", back_populates="section")
    
    
class Dependency(BaseClass):
    __tablename__ = "dependency"
    
    section_id = Column(Integer, ForeignKey("section.id"), nullable=False)
    depends_on = Column(Integer, ForeignKey("section.id"), nullable=False)
    
    section = relationship("Section", foreign_keys=[section_id], back_populates="dependencies")
    depends_on_section = relationship("Section", foreign_keys=[depends_on])
    
    
class Restriction(BaseClass):
    __tablename__ = "restriction"
    
    name = Column(String, nullable=False)
    prompt = Column(String, nullable=False)
    section_id = Column(Integer, ForeignKey("section.id"), nullable=False)
    
    section = relationship("Section", back_populates="restrictions")
    evaluations = relationship("Evaluation", back_populates="restriction")
    

class Document(BaseClass):
    __tablename__ = "document"
    
    name = Column(String, nullable=False)
    template_id = Column(Integer, ForeignKey("template.id"), nullable=False)
    template = relationship("Template", back_populates="documents")
    executions = relationship("Execution", back_populates="document")
    
class Status(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"    

class Execution(BaseClass):
    __tablename__ = "execution"
    
    status = Column(SAEnum(Status, name="status_enum"), nullable=False)
    status_message = Column(String, nullable=True)
    document_id = Column(Integer, ForeignKey("document.id"), nullable=False)
    
    document = relationship("Document", back_populates="executions")
    sections = relationship("SectionExecution", back_populates="execution")
    

class SectionExecution(BaseClass):
    __tablename__ = "section_execution"

    output = Column(String, nullable=True)
    section_id = Column(Integer, ForeignKey("section.id"), nullable=False)
    execution_id = Column(Integer, ForeignKey("execution.id"), nullable=False)
    
    section = relationship("Section", back_populates="executions")
    execution = relationship("Execution", back_populates="sections")
    evaluations = relationship("Evaluation", back_populates="section_execution")
    
class Evaluation(BaseClass):
    __tablename__ = "evaluation"
    
    result = Column(String, nullable=False)
    justification = Column(String, nullable=True)
    section_execution_id = Column(Integer, ForeignKey("section_execution.id"), nullable=False)
    restriction_id = Column(Integer, ForeignKey("restriction.id"), nullable=False)
    
    section_execution = relationship("SectionExecution", back_populates="evaluations")
    restriction = relationship("Restriction", back_populates="evaluations")

    
    
    
    
