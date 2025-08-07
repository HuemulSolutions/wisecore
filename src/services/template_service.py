from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repositories.template_repo import TemplateRepo
from src.database.repositories.organization_repo import OrganizationRepo
from src.database.models import Template

class TemplateService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.template_repo = TemplateRepo(session)
        self.organization_repo = OrganizationRepo(session)
        
    async def get_template_by_id(self, template_id: str) -> Template:
        """
        Retrieve a template by its ID.
        """
        template = await self.template_repo.get_by_id(template_id)
        if not template:
            raise ValueError(f"Template with ID {template_id} not found.")
        return template
    

    async def create_template(self, name: str, organization_id: str, description: str) -> Template:
        """
        Create a new template.
        """
        template = await self.template_repo.get_by_name(name)
        if template:
            raise ValueError(f"Template with name {name} already exists.")
        
        if not await self.organization_repo.get_by_id(organization_id):
            raise ValueError(f"Organization with ID {organization_id} not found.")
        new_template = Template(name=name, organization_id=organization_id, description=description)
        created_template = await self.template_repo.add(new_template)
        return created_template
    
    async def get_all_templates(self) -> list[Template]:
        """
        Retrieve all templates.
        """
        return await self.template_repo.get_all()
    
    async def delete_template(self, template_id: str) -> None:
        """
        Delete a template by its ID.
        """
        template = await self.template_repo.get_by_id(template_id)
        if not template:
            raise ValueError(f"Template with ID {template_id} not found.")
        await self.template_repo.delete(template)
    
    async def export_template(self, template_id: str) -> dict:
        """
        Export a template to a JSON-compatible dictionary format.
        Excludes internal IDs, creation dates, and other metadata.
        """
        template = await self.template_repo.get_by_id(template_id)
        if not template:
            raise ValueError(f"Template with ID {template_id} not found.")
        
        # Build the export structure
        export_data = {
            "name": template.name,
            "description": template.description,
            "sections": []
        }
        
        # Add sections with their dependencies
        for section in template.template_sections:
            section_data = {
                "name": section.name,
                "type": section.type,
                "order": section.order,
                "prompt": section.prompt,
                "dependencies": [dep.depends_on_template_section.name for dep in section.internal_dependencies]
            }
            export_data["sections"].append(section_data)
        
        return export_data