from sqlalchemy.ext.asyncio import AsyncSession
from .repository import DocumentRepo
# from src.database.repositories.inner_depend_repo import InnerDependencyRepo
# from src.database.repositories.dependency_repo import DependencyRepo
from .models import Document
from .models import Document, Dependency
from src.modules.execution.models import Execution, Status
from src.modules.section.models import Section
from src.modules.generation.service import generate_document_structure
from src.modules.template.service import TemplateService
from src.modules.section.service import SectionService
from src.modules.organization.service import OrganizationService
from src.modules.document_type.service import DocumentTypeService

class DocumentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.document_repo = DocumentRepo(session)

    async def get_document_by_id(self, document_id: str):
        """
        Retrieve a document by its ID.
        """
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            raise ValueError(f"Document with ID {document_id} not found.")
        return document
    
    async def get_document(self, document_id: str)-> Document:
        """
        Retrieve a document by its ID.
        """
        document = await self.document_repo.get_document(document_id)
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
    
    async def update_document(self, document_id: str, name: str = None, description: str = None):
        """
        Update a document's name and/or description.
        """
        document = await self.document_repo.get_document(document_id)
        if not document:
            raise ValueError(f"Document with ID {document_id} not found.")
        
        # Check if name is being updated and if it already exists
        if name and name != document.name:
            existing_document = await self.document_repo.get_by_name(name)
            if existing_document:
                raise ValueError(f"Document with name {name} already exists.")
            document.name = name
        
        if description is not None:
            document.description = description
        
        updated_document = await self.document_repo.update(document)
        return updated_document
    
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
        
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            raise ValueError(f"Document with ID {document_id} not found.")
        
        section_service = SectionService(self.session)
        sections = await section_service.get_document_sections(document_id)
        return sections
    
    async def create_document(self, name: str, description: str, organization_id: str, 
                              document_type_id: str, template_id: str = None,
                              folder_id: str = None):
        """
        Create a new document.
        """
        organization_service = OrganizationService(self.session)
        if not await organization_service.check_organization_exists(organization_id):
            raise ValueError(f"Organization with ID {organization_id} not found.")
        
        template_service = TemplateService(self.session)
        if template_id and not await template_service.template_exists(template_id):
            raise ValueError(f"Template with ID {template_id} not found.")
        
        if document_type_id:
            document_type_service = DocumentTypeService(self.session)
            if not await document_type_service.check_if_document_type_exists(document_type_id):
                raise ValueError(f"Document type with ID {document_type_id} not found.")
        
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
        template_service = TemplateService(self.session)
        template_sections = await template_service.get_template_sections(template_id)
        
        # Create a mapping from template_section_id to new section_id
        template_to_section_mapping = {}
        
        # First pass: create all sections
        section_service = SectionService(self.session)
        for template_section in template_sections:
            new_section = Section(
                name=template_section.name,
                type=template_section.type,
                prompt=template_section.prompt,
                order=template_section.order,
                document_id=document_id,
                template_section_id=template_section.id
            )
            new_section = await section_service.add_section_object(new_section)
            template_to_section_mapping[template_section.id] = new_section.id
        
        # Second pass: create internal dependencies
        for template_section in template_sections:
            if hasattr(template_section, 'internal_dependencies') and template_section.internal_dependencies:
                for template_dependency in template_section.internal_dependencies:
                    section_id = template_to_section_mapping[template_section.id]
                    depends_on_section_id = template_to_section_mapping[template_dependency.depends_on_template_section_id]
                    
                    await section_service.add_dependency(section_id, depends_on_section_id)
                    # inner_dependency = InnerDependency(
                    #     section_id=section_id,
                    #     depends_on_section_id=depends_on_section_id
                    # )
                    # await self.inner_dependency_repo.add(inner_dependency)
        
        # Commit all changes
        await self.session.flush()
                
    
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
        section_service = SectionService(self.session)
        
        existing_sections = await section_service.get_document_sections(document_id)
        if existing_sections:
            raise ValueError("Document already has sections. Cannot save generated structure.")
        
        sections = structure.get("sections", [])
        if not sections:
            raise ValueError("No sections found in the structure.")
        
        # Create a mapping from section name to Section object
        section_map = {}
        
        section_service = SectionService(self.session)
        for section_data in sections:
            section = Section(
                name=section_data["name"],
                type="text",
                order=section_data["order"],
                prompt=section_data["prompt"],
                document_id=document_id
            )
            created_section = await section_service.add_section_object(section)
            section_map[section_data["name"]] = created_section
        
        # Then, create internal dependencies
        for section_data in sections:
            current_section = section_map[section_data["name"]]
            dependencies = section_data.get("dependencies", [])
            
            for dependency_name in dependencies:
                if dependency_name not in section_map:
                    raise ValueError(f"Dependency '{dependency_name}' not found for section '{section_data['name']}'")
                
                dependency_section = section_map[dependency_name]
                
                await section_service.add_dependency(current_section.id, dependency_section.id)
                # inner_dependency = InnerDependency(
                #     section_id=current_section.id,
                #     depends_on_section_id=dependency_section.id
                # )
                # await self.inner_dependency_repo.add(inner_dependency)

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

    async def get_document_dependencies(self, document_id: str):
        """
        Retrieve all dependencies for a specific document.
        """
        if not await self.document_repo.get_by_id(document_id):
            raise ValueError(f"Document with ID {document_id} not found.")
        
        dependencies = await self.document_repo.get_dependencies(document_id)
        return dependencies

    async def add_document_dependency(self, document_id: str, depends_on_document_id: str, 
                                      section_id: str = None, depends_on_section_id: str = None):
        """
        Add a dependency relationship between two full documents or specific sections.
        """
        if not await self.document_repo.get_by_id(document_id):
            raise ValueError(f"Document with ID {document_id} not found.")
        if not await self.document_repo.get_by_id(depends_on_document_id):
            raise ValueError(f"Document with ID {depends_on_document_id} not found.")
        
        section_service = SectionService(self.session)
        if section_id:
            await section_service.get_section_by_id(section_id)
            
        if depends_on_section_id:
            await section_service.get_section_by_id(depends_on_section_id)

        # Create the dependency
        new_dependency = Dependency(
            document_id=document_id,
            section_id=section_id,
            depends_on_document_id=depends_on_document_id,
            depends_on_section_id=depends_on_section_id
        )
        await self.document_repo.add_dependency(new_dependency)
        return new_dependency
    
    async def delete_document_dependency(self, document_id: str, depends_on_document_id: str):
        """
        Remove a dependency relationship between two documents.
        """
        if not await self.document_repo.get_by_id(document_id):
            raise ValueError(f"Document with ID {document_id} not found.")
        if not await self.document_repo.get_by_id(depends_on_document_id):
            raise ValueError(f"Document with ID {depends_on_document_id} not found.")
        
        # Find and delete the dependency
        dependency = await self.document_repo.get_dependency_by_ids(document_id, depends_on_document_id)
        if not dependency:
            raise ValueError(f"No dependency found between {document_id} and {depends_on_document_id}.")
        
        await self.document_repo.delete_dependency(dependency)
        return {"message": "Dependency removed successfully."}
    
    async def get_document_context(self, document_id: str):
        """
        Retrieve the context associated with a document.
        """
        context = await self.document_repo.get_document_context(document_id)
        return context

