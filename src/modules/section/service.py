from sqlalchemy.ext.asyncio import AsyncSession
from .repository import SectionRepo
from .models import Section

class SectionService:
    def __init__(self, session: AsyncSession):
        self.session = session        
        self.section_repo = SectionRepo(session)
        
    async def create_section(self, name: str, document_id: str,
                                prompt: str, type: str, dependencies: list[str]) -> Section:
        """
        Create a new template section.
        """
        document = await self.section_repo.check_if_document_exists(document_id)
        if not document:
            raise ValueError(f"Document with ID {document_id} not found.")
        
        check_name = await self.section_repo.get_by_name_and_document_id(name, document_id)
        if check_name:
            raise ValueError(f"Document section with name {name} already exists in this document.")

        sections = await self.section_repo.get_sections_by_doc_id(document_id)
        last_order = sections[-1].order if sections else 0
        order = last_order + 1
        
        
        new_section = Section(name=name, document_id=document_id,
                                     order=order, prompt=prompt, type=type)
        created_section = await self.section_repo.add(new_section, dependencies=dependencies)
        return created_section
    
    async def add_section_object(self, section: Section) -> Section:
        """
        Add an existing Section object to the database.
        """
        created_section = await self.section_repo.add(section)
        return created_section
    
    async def get_document_sections(self, document_id: str):
        """
        Retrieve all sections for a specific document.
        """
        sections = await self.section_repo.get_sections_by_doc_id(document_id)
        return sections
    
    
    async def get_document_sections_graph(self, document_id: str):
        """
        Retrieve all sections for a specific document for graph processing.
        """
        sections = await self.section_repo.get_sections_by_doc_id_graph(document_id)
        return sections
    
    async def get_section_by_id(self, section_id: str) -> Section:
        """
        Retrieve a section by its ID.
        """
        section = await self.section_repo.get_by_id(section_id)
        if not section:
            raise ValueError(f"Section with ID {section_id} not found.")
        return section
    
    
    async def add_dependency(self, section_id: str, depends_on_id: str) -> Section:
        """
        Add a dependency relationship between two template sections.
        """
        return await self.section_repo.add_dependency(section_id, depends_on_id)
    
    async def update_section(self, section_id: str, name: str = None, prompt: str = None,
                             dependencies: list[str] = None) -> Section:
        """
        Update an existing section.
        """
        section = await self.section_repo.get_by_id(section_id)
        if not section:
            raise ValueError(f"Section with ID {section_id} not found.")
        
        if name:
            section.name = name
        if prompt:
            section.prompt = prompt
        
        updated_section = await self.section_repo.update_section(section, dependencies=dependencies)
        return updated_section
    
    async def delete_section(self, section_id: str) -> None:
        """
        Delete a section.
        """
        section = await self.section_repo.get_by_id(section_id)
        if not section:
            raise ValueError(f"Section with ID {section_id} not found.")
        
        await self.section_repo.delete(section)
    
    async def update_section_order(self, new_order: list[dict]) -> Section:
        """
        Update the order of a section.
        """
        updated_sections = []
        for item in new_order:
            section = await self.section_repo.get_by_id(item.section_id)
            if not section:
                raise ValueError(f"Section with ID {item['section_id']} not found.")
            section.order = item.order
            updated_section = await self.section_repo.update(section)
            updated_sections.append(updated_section)
        
        return updated_sections
    
    async def check_section_exists(self, section_id: str, document_id: str) -> bool:
        """
        Check if a section exists for a given document.
        """
        section = await self.section_repo.get_by_id_and_document_id(section_id, document_id)
        return section is not None
        