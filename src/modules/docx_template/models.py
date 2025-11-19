from src.database.base_model import BaseModel
from sqlalchemy import Column, String, ForeignKey, Integer, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

class DocxTemplate(BaseModel):
    __tablename__ = "docx_template"
    
    name = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    mime_type = Column(String, nullable=False, default='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    file_size = Column(Integer, nullable=False)
    file_data = Column(LargeBinary, nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("document.id"), nullable=False)
    
    document = relationship("Document", back_populates="docx_template")
    