from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repositories.section_repo import SectionRepo
from src.database.repositories.document_repo import DocumentRepo
from src.database.models import Section

class SectionService:
    def __init__(self, session: AsyncSession):
        self.session = session        
        self.document_repo = DocumentRepo(session)
        self.section_repo = SectionRepo(session)
        
    async def create_section(self, name: str, document_id: str,
                                prompt: str, type: str, dependencies: list[str]) -> Section:
        """
        Create a new template section.
        """
        document = await self.document_repo.get_document(document_id)
        if not document:
            raise ValueError(f"Template not found.")
        
        check_name = await self.section_repo.get_by_name_and_document_id(name, document_id)
        if check_name:
            raise ValueError(f"Document section with name {name} already exists in this document.")

        
        last_order = document.sections[-1].order if document.sections else 0
        order = last_order + 1
        
        
        new_section = Section(name=name, document_id=document_id,
                                     order=order, prompt=prompt, type=type)
        created_section = await self.section_repo.add(new_section, dependencies=dependencies)
        return created_section
    
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
        