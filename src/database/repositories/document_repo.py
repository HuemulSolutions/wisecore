from .base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Document, InnerDependency, Section, Execution, Status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID

class DocumentRepo(BaseRepository[Document]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Document)
        
    async def get_all_documents(self, organization_id: str = None, document_type_id: str = None) -> list[dict]:
        """
        Retrieve all documents with optional pagination, including template name.
        """
        query = select(self.model).options(
            selectinload(Document.template),
            selectinload(Document.document_type)
            )
        
        if organization_id:
            query = query.where(self.model.organization_id == organization_id)
            
        if document_type_id:
            query = query.where(self.model.document_type_id == document_type_id)
            
        query = query.order_by(self.model.created_at.desc())
        result = await self.session.execute(query)
        documents = result.scalars().all()
        return [
            {
                **doc.__dict__,
                'template_name': doc.template.name if doc.template else None,
                'document_type': {
                    'id': doc.document_type.id,
                    'name': doc.document_type.name,
                    'color': doc.document_type.color
                } if doc.document_type else None
                
            }
            for doc in documents
        ]
    
    async def get_by_name(self, name: str) -> Document:
        """
        Retrieve a document by its name.
        """
        query = select(self.model).where(self.model.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_id(self, document_id: UUID) -> dict:
        """
        Retrieve a document by its ID with template name and executions info.
        """
        query = (
            select(self.model)
            .options(
                selectinload(Document.organization),
                selectinload(Document.template),
                selectinload(Document.executions),
                selectinload(Document.document_type),
                selectinload(Document.sections)
                .selectinload(Section.internal_dependencies)
                .selectinload(InnerDependency.depends_on_section)
            )
            .where(self.model.id == document_id)
        )
        result = await self.session.execute(query)
        doc = result.scalar_one_or_none()
        
        if not doc:
            return None
        
        sorted_executions = sorted(doc.executions, key=lambda e: e.created_at, reverse=True)
        sorted_sections = sorted(doc.sections, key=lambda s: s.order)
            
        return {
            "id": doc.id,
            "name": doc.name,
            "description": doc.description,
            "organization_id": doc.organization_id,
            "organization": doc.organization.name,
            "template_id": doc.template_id,
            "template_name": doc.template.name if doc.template else None,
            "created_at": doc.created_at,
            "updated_at": doc.updated_at,
            "document_type": {
                "id": doc.document_type.id,
                "name": doc.document_type.name,
                "color": doc.document_type.color
            },
            "executions": [
                {
                    "id": execution.id,
                    "status": execution.status.value,
                    "status_message": execution.status_message,
                    "created_at": execution.created_at,
                }
                for execution in sorted_executions
            ],
            "sections": [
                {
                    "id": section.id,
                    "name": section.name,
                    "prompt": section.prompt,
                    "order": section.order,
                    "dependencies": [
                       {"id": dep.depends_on_section_id, "name": dep.depends_on_section.name} for dep in section.internal_dependencies
                    ]
                }
                for section in sorted_sections
            ]
        }
    
    async def get_document(self, document_id: UUID) -> Document:
        """
        Retrieve a document by its ID with sections and dependencies.
        """
        query = (
            select(self.model)
            .options(
                selectinload(Document.sections)
                .selectinload(Section.internal_dependencies)
                .selectinload(InnerDependency.depends_on_section)
            )
            .where(self.model.id == document_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_document_content(self, document_id: str, execution_id: str = None) -> tuple[str, str]:
        """
        Retrieve the content of a document by its ID.
        Returns a tuple with (execution_id, content).
        If execution_id is provided, uses that specific execution if it's approved or completed.
        Otherwise, uses the default logic to find approved or latest completed execution.
        """
        query = (
            select(self.model)
            .options(
                selectinload(Document.sections)
                .selectinload(Section.section_executions),
                selectinload(Document.executions)
            )
            .where(self.model.id == document_id)
        )
        result = await self.session.execute(query)
        document = result.scalar_one_or_none()
        
        if not document:
            raise ValueError(f"Document with ID {document_id} not found.")
        
        if not document.executions:
            return None, None
        
        target_execution = None
        
        if execution_id:
            # Find specific execution if provided
            for execution in document.executions:
                if str(execution.id) == execution_id:
                    if execution.status in [Status.APPROVED, Status.COMPLETED]:
                        target_execution = execution
                    break
        else:
            # Find approved execution or latest completed execution
            approved_execution = None
            latest_completed_execution = None
            
            for execution in document.executions:
                if execution.status == Status.APPROVED:
                    approved_execution = execution
                    break
                elif execution.status == Status.COMPLETED:
                    if not latest_completed_execution or execution.created_at > latest_completed_execution.created_at:
                        latest_completed_execution = execution
            
            target_execution = approved_execution or latest_completed_execution
        
        if not target_execution:
            print("NO TARGET EXECUTION")
            return None, None
        
        content = ""
        sections = sorted(document.sections, key=lambda s: s.order)
        for section in sections:
            # Get section execution from target execution
            section_execution = None
            for sec_exec in section.section_executions:
                if sec_exec.execution_id == target_execution.id:
                    section_execution = sec_exec
                    break
            
            if section_execution:
                if section_execution.custom_output:
                    section_content = section_execution.custom_output
                elif section_execution.output:
                    section_content = section_execution.output
                else:
                    continue
                content += f"{section_content}\n\n"
        
        final_content = content.strip() if content.strip() else None
        return str(target_execution.id), final_content
    
    async def get_document_context(self, document_id: UUID) -> str:
        """
        Retrieve the document context and  external dependencies.
        """
        query = (
            select(self.model)
            .options(
                selectinload(Document.contexts),
                selectinload(Document.dependencies)
            )
            .where(self.model.id == document_id)
        )
        result = await self.session.execute(query)
        document = result.scalar_one_or_none()
        
        if not document:
            raise ValueError(f"Document with ID {document_id} not found.")
        
        context_str = ""
        for context in document.contexts:
            context_str += f"# {context.name}\n\n {context.content}\n"
        
        for dependency in document.dependencies:
            dependency_content = await self.get_document_content(dependency.depends_on_document_id)
            context_str += f"{dependency_content}\n"
        return context_str
                
        
        
    