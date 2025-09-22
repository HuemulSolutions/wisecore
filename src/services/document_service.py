from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repositories.document_repo import DocumentRepo
from src.database.repositories.section_repo import SectionRepo
from src.database.repositories.template_repo import TemplateRepo
from src.database.repositories.inner_depend_repo import InnerDependencyRepo
from src.database.repositories.dependency_repo import DependencyRepo
from src.database.repositories.execution_repo import ExecutionRepo
from src.database.repositories.context_repo import ContextRepo
from src.database.repositories.organization_repo import OrganizationRepo
from src.database.models import (Document, Section, InnerDependency, Execution, Status)
from src.services.generation_service import generate_document_structure

class DocumentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.document_repo = DocumentRepo(session)
        self.section_repo = SectionRepo(session)
        self.template_repo = TemplateRepo(session)
        self.inner_dependency_repo = InnerDependencyRepo(session)
        self.dependency_repo = DependencyRepo(session)
        self.execution_repo = ExecutionRepo(session)
        self.context_repo = ContextRepo(session)
        self.organization_repo = OrganizationRepo(session)

    async def get_document_by_id(self, document_id: str):
        """
        Retrieve a document by its ID.
        """
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            raise ValueError(f"Document with ID {document_id} not found.")
        return document
    
    async def delete_document(self, document_id: str):
        """
        Delete a document by its ID.
        """
        document = await self.document_repo.get_document(document_id)
        if not document:
            raise ValueError(f"Document with ID {document_id} not found.")
        await self.document_repo.delete(document)
        return True
    
    async def get_all_documents(self, organization_id: str = None, document_type_id: str = None):
        """
        Retrieve all documents.
        """
        documents = await self.document_repo.get_all_documents(organization_id, document_type_id)
        return documents
    
    async def get_document_sections(self, document_id: str):
        """
        Retrieve all sections for a specific document.
        """
        sections = await self.section_repo.get_sections_by_doc_id(document_id)
        return sections
    
    async def create_document(self, name: str, description: str, organization_id: str, 
                              document_type_id: str, template_id: str = None,
                              folder_id: str = None):
        """
        Create a new document.
        """
        print("Checking if template_id is provided:", template_id)
        if await self.organization_repo.get_by_id(organization_id) is None:
            raise ValueError(f"Organization with ID {organization_id} not found.")
        
        if template_id and not await self.template_repo.get_by_id(template_id):
            raise ValueError(f"Template with ID {template_id} not found.")
        
        if await self.document_repo.get_by_name(name):
            raise ValueError(f"Document with name {name} already exists.")
        
        new_document = Document(name=name, description=description,
                                organization_id=organization_id,
                                document_type_id=document_type_id,
                                template_id=template_id, folder_id=folder_id)
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
    
    
    async def get_document_content(self, document_id: str, execution_id: str = None):
        """
        Retrieve the content of a document by its ID.
        Check if there is an approved execution; if not, it retrives the latest completed execution.
        """
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            raise ValueError(f"Document with ID {document_id} not found.")
        
        content = None
        execution_id, content = await self.document_repo.get_document_content(document_id, execution_id)
        response = {
            "document_id": document['id'],
            "execution_id": execution_id,
            "document_type": document["document_type"],
            "executions": document["executions"],
            "content": content
        }
        return response
    
    async def save_generated_structure(self, document_id: str, structure: dict):
        """
        Save a generated structure to a document.
        """
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            raise ValueError(f"Document with ID {document_id} not found.")
        
        # Check if document already has sections
        existing_sections = await self.section_repo.get_sections_by_doc_id(document_id)
        if existing_sections:
            raise ValueError("Document already has sections. Cannot save generated structure.")
        
        sections = structure.get("sections", [])
        if not sections:
            raise ValueError("No sections found in the structure.")
        
        # Create a mapping from section name to Section object
        section_map = {}
        
        # First, create all sections
        for section_data in sections:
            section = Section(
                name=section_data["name"],
                type="text",
                order=section_data["order"],
                prompt=section_data["prompt"],
                document_id=document_id
            )
            created_section = await self.section_repo.add(section)
            section_map[section_data["name"]] = created_section
        
        # Then, create internal dependencies
        for section_data in sections:
            current_section = section_map[section_data["name"]]
            dependencies = section_data.get("dependencies", [])
            
            for dependency_name in dependencies:
                if dependency_name not in section_map:
                    raise ValueError(f"Dependency '{dependency_name}' not found for section '{section_data['name']}'")
                
                dependency_section = section_map[dependency_name]
                inner_dependency = InnerDependency(
                    section_id=current_section.id,
                    depends_on_section_id=dependency_section.id
                )
                await self.inner_dependency_repo.add(inner_dependency)

        # Flush changes to database
        await self.session.flush()
        
        return document
    
    async def generate_document_structure(self, document_id: str):
        """
        Generate the structure of a document based on its template.
        """
        document = await self.document_repo.get_document(document_id)
        if not document:
            raise ValueError(f"Document with ID {document_id} not found.")
        

        structure = await generate_document_structure(document.name, document.description)
        
        document = await self.save_generated_structure(document_id, structure)
        return document

