from src.database.base_model import BaseModel
from sqlalchemy import Column, String, ForeignKey, Integer, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

class Document(BaseModel):
    __tablename__ = "document"
    
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("template.id"), nullable=True)
    document_type_id = Column(UUID(as_uuid=True), ForeignKey("document_type.id"), nullable=False)
    folder_id = Column(UUID(as_uuid=True), ForeignKey("folder.id"), nullable=True)
    
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
    
    
class Dependency(BaseModel):
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

