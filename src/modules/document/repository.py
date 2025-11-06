from typing import Optional
from src.database.base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Document, Dependency
from src.modules.execution.models import Status
from src.modules.section.models import Section, InnerDependency
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

    async def get_by_name_in_folder(
        self,
        name: str,
        organization_id: UUID,
        folder_id: Optional[UUID],
        exclude_id: Optional[UUID] = None,
    ) -> Document:
        """
        Retrieve a document by name scoped to an organization and folder.
        Optionally exclude a specific document (useful when updating).
        """
        query = (
            select(self.model)
            .where(self.model.name == name)
            .where(self.model.organization_id == organization_id)
        )

        if folder_id is None:
            query = query.where(self.model.folder_id.is_(None))
        else:
            query = query.where(self.model.folder_id == folder_id)

        if exclude_id:
            query = query.where(self.model.id != exclude_id)

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
                selectinload(Document.docx_template),
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
            "docx_template": doc.docx_template[0].name if doc.docx_template else None,
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
    
    async def get_document_content(self, document_id: str, execution_id: str = None) -> tuple[str, list[dict]]:
        """
        Retrieve the content of a document by its ID.
        Returns a tuple with (execution_id, content).
        If execution_id is provided, uses that specific execution if it's approved or completed.
        Otherwise, uses the default logic to find approved or latest completed execution.
        Content is now a list of dictionaries with section_execution_id and content.
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
        
        content_list = []
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
                
                content_list.append({
                    "id": str(section_execution.id),
                    "content": section_content
                })
        
        final_content = content_list if content_list else None
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
    
    async def add_dependency(self, dependency: Dependency) -> Dependency:
        """
        Add a new dependency to the document.
        """
        self.session.add(dependency)
        await self.session.flush()
        return dependency
    
    async def delete_dependency(self, dependency: Dependency) -> None:
        """
        Delete a dependency from the document.
        """
        await self.session.delete(dependency)
        await self.session.flush()
    
    async def get_dependencies(self, document_id: UUID) -> list[dict]:
        """
        Retrieve all documents that the given document depends on.
        Returns dependencies both at document level and section level.
        """
        query = (
            select(Dependency)
            .options(
                selectinload(Dependency.depends_on),
                selectinload(Dependency.depends_on_section)
            )
            .where(Dependency.document_id == document_id)
        )
        result = await self.session.execute(query)
        dependencies = result.scalars().all()
        
        return [
            {
                "document_id": dep.depends_on.id,
                "document_name": dep.depends_on.name,
                "section_name": dep.depends_on_section.name if dep.depends_on_section else None,
                "dependency_type": "section" if dep.depends_on_section else "document"
            }
            for dep in dependencies
        ]
    
    async def get_dependency_by_ids(self, document_id: UUID, depends_on_document_id: UUID) -> Dependency:
        """
        Retrieve a specific dependency by document and its dependent document IDs.
        """
        query = (
            select(Dependency)
            .where(
                Dependency.document_id == document_id,
                Dependency.depends_on_document_id == depends_on_document_id
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
