from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repositories.document_repo import DocumentRepo
from src.database.repositories.section_repo import SectionRepo
from src.database.repositories.template_repo import TemplateRepo
from src.database.repositories.inner_depend_repo import InnerDependencyRepo
from src.database.repositories.dependency_repo import DependencyRepo
from src.database.repositories.execution_repo import ExecutionRepo
from src.database.repositories.sectionexec_repo import SectionExecRepo
from src.database.models import (Document, Section, InnerDependency, 
                                 Dependency, Execution, Status, SectionExecution)

class DocumentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.document_repo = DocumentRepo(session)
        self.section_repo = SectionRepo(session)
        self.template_repo = TemplateRepo(session)
        self.inner_dependency_repo = InnerDependencyRepo(session)
        self.dependency_repo = DependencyRepo(session)
        self.execution_repo = ExecutionRepo(session)

    async def get_document_by_id(self, document_id: str):
        """
        Retrieve a document by its ID.
        """
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            raise ValueError(f"Document with ID {document_id} not found.")
        return document
    
    async def get_all_documents(self):
        """
        Retrieve all documents.
        """
        documents = await self.document_repo.get_all_documents()
        return documents
    
    async def get_document_sections(self, document_id: str):
        """
        Retrieve all sections for a specific document.
        """
        sections = await self.section_repo.get_sections_by_doc_id(document_id)
        if not sections:
            raise ValueError(f"No sections found for document ID {document_id}.")
        return sections
    
    async def create_document(self, name: str, description: str, template_id: str = None):
        """
        Create a new document.
        """
        print("Checking if template_id is provided:", template_id)
        if template_id and not await self.template_repo.get_by_id(template_id):
            raise ValueError(f"Template with ID {template_id} not found.")
        
        if await self.document_repo.get_by_name(name):
            raise ValueError(f"Document with name {name} already exists.")
        
        new_document = Document(name=name, description=description, template_id=template_id)
        await self.document_repo.add(new_document)
        
        # If template_id is provided, copy template sections to document sections
        if template_id:
            await self._copy_template_sections_to_document(template_id, new_document.id)
        
        return new_document

    async def _copy_template_sections_to_document(self, template_id: str, document_id: str):
        """
        Copy template sections and their dependencies to a document.
        """
        # Get template sections
        template_sections = await self.template_repo.get_template_sections(template_id)
        
        # Create a mapping from template_section_id to new section_id
        template_to_section_mapping = {}
        
        # First pass: create all sections
        for template_section in template_sections:
            new_section = Section(
                name=template_section.name,
                type=template_section.type,
                prompt=template_section.prompt,
                order=template_section.order,
                document_id=document_id,
                template_section_id=template_section.id
            )
            await self.section_repo.add(new_section)
            template_to_section_mapping[template_section.id] = new_section.id
        
        # Second pass: create internal dependencies
        for template_section in template_sections:
            if hasattr(template_section, 'internal_dependencies') and template_section.internal_dependencies:
                for template_dependency in template_section.internal_dependencies:
                    section_id = template_to_section_mapping[template_section.id]
                    depends_on_section_id = template_to_section_mapping[template_dependency.depends_on_template_section_id]
                    
                    inner_dependency = InnerDependency(
                        section_id=section_id,
                        depends_on_section_id=depends_on_section_id
                    )
                    await self.inner_dependency_repo.add(inner_dependency)
        
        # Commit all changes
        await self.session.flush()
        
    async def create_document_section(self, document_id: str, name: str, order: int,
                                      type: str, prompt: str = None, content: str = None):
        """
        Create a new section in a document.
        """
        if not await self.document_repo.get_by_id(document_id):
            raise ValueError(f"Document with ID {document_id} not found.")
        if await self.section_repo.get_by_name_and_document_id(name, document_id):
            raise ValueError(f"Section with name {name} already exists in document ID {document_id}.")
        if await self.section_repo.get_by_order_and_document_id(order, document_id):
            raise ValueError(f"Section with order {order} already exists in document ID {document_id}.")
        
        new_section = Section(
            name=name,
            order=order,
            type=type,
            prompt=prompt,
            document_id=document_id
        )
        new_section = await self.section_repo.add(new_section)
        if content:
            execution = await self._create_or_get_execution_for_content(document_id)
            new_section_execution = SectionExecution(
                section_id=new_section.id,
                execution_id=execution.id,
                output=content
            )
            await self.section_repo.add(new_section_execution)
        return new_section
                
            
    async def _create_or_get_execution_for_content(self, document_id: str):
        executions = await self.execution_repo.get_executions_by_doc_id(document_id)
        if executions:
            # If there are existing executions, return the most recent one
            return executions[-1]
        # If no executions exist, create a new one
        new_execution = Execution(
            document_id=document_id,
            status=Status.APPROVED
        )
        new_execution = await self.execution_repo.add(new_execution)
        return new_execution
            
        

    async def add_document_dependency(self, document_id: str, depends_on_document_id: str, 
                                      section_id: str = None, depends_on_section_id: str  = None):
        """
        Add a dependency relationship between two full documents or specific sections.
        """
        if not await self.document_repo.get_by_id(document_id):
            raise ValueError(f"Document with ID {document_id} not found.")
        if not await self.document_repo.get_by_id(depends_on_document_id):
            raise ValueError(f"Document with ID {depends_on_document_id} not found.")
        if section_id and not await self.section_repo.get_by_id(section_id):
            raise ValueError(f"Section with ID {section_id} not found in document {document_id}.")
        if depends_on_section_id and not await self.section_repo.get_by_id(depends_on_section_id):
            raise ValueError(f"Section with ID {depends_on_section_id} not found in document {depends_on_document_id}.")
        
        # Create the dependency
        new_dependency = Dependency(
            document_id=document_id,
            section_id=section_id,
            depends_on_document_id=depends_on_document_id,
            depends_on_section_id=depends_on_section_id
        )
        await self.dependency_repo.add(new_dependency)
        return new_dependency
        