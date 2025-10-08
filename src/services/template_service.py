from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repositories.template_repo import TemplateRepo
from src.database.repositories.template_section_repo import TemplateSectionRepo
from src.database.repositories.template_section_dep_repo import TemplateSectionDepRepo
from src.database.repositories.organization_repo import OrganizationRepo
from src.database.models import Template, TemplateSection, TemplateSectionDependency
from src.services.generation_service import generate_document_structure

class TemplateService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.template_repo = TemplateRepo(session)
        self.template_section_repo = TemplateSectionRepo(session)
        self.template_section_dep_repo = TemplateSectionDepRepo(session)
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
        template = await self.template_repo.get_by_name(name, organization_id=organization_id)
        if template:
            raise ValueError(f"Template with name {name} already exists.")
        
        if not await self.organization_repo.get_by_id(organization_id):
            raise ValueError(f"Organization with ID {organization_id} not found.")
        new_template = Template(name=name, organization_id=organization_id, description=description)
        created_template = await self.template_repo.add(new_template)
        return created_template
    
    async def get_all_templates(self, organization_id: str) -> list[Template]:
        """
        Retrieve all templates.
        """
        return await self.template_repo.get_templates(organization_id)
    
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
    
    async def save_generated_structure(self, template_id: str, structure: dict) -> Template:
        """
        Save a generated structure to a template.
        """
        template = await self.template_repo.get_by_id(template_id)
        if not template:
            raise ValueError(f"Template with ID {template_id} not found.")
        
        if len(template.template_sections) > 0:
            raise ValueError("Template already has sections. Cannot save generated structure.")
        
        sections = structure.get("sections", [])
        if not sections:
            raise ValueError("No sections found in the structure.")
        
        # Crear un mapeo de nombre de sección a objeto TemplateSection
        section_map = {}
        
        # Primero crear todas las secciones
        for section_data in sections:
            template_section = TemplateSection(
                name=section_data["name"],
                type="text",
                order=section_data["order"],
                prompt=section_data["prompt"],
                template_id=template_id
            )
            created_section = await self.template_section_repo.add(template_section)
            section_map[section_data["name"]] = created_section
        
        # Luego crear las dependencias
        for section_data in sections:
            current_section = section_map[section_data["name"]]
            dependencies = section_data.get("dependencies", [])
            
            for dependency_name in dependencies:
                if dependency_name not in section_map:
                    raise ValueError(f"Dependency '{dependency_name}' not found for section '{section_data['name']}'")
                
                dependency_section = section_map[dependency_name]
                template_section_dependency = TemplateSectionDependency(
                    template_section_id=current_section.id,
                    depends_on_template_section_id=dependency_section.id
                )
                await self.template_section_dep_repo.add(template_section_dependency)

        
        # Refrescar el template para obtener las secciones actualizadas
        await self.session.refresh(template)
        return template
    
    async def generate_template_structure(self, template_id: str):
        """
        Auto-generate a template structure based on the template's name and description.
        """
        template = await self.template_repo.get_by_id(template_id)
        if not template:
            raise ValueError(f"Template with ID {template_id} not found.")
        if len(template.template_sections) > 0:
            raise ValueError("Template already has sections. Cannot auto-generate structure.")
        
        structure = await generate_document_structure(template.name, template.description)
        template = await self.save_generated_structure(template_id, structure)
        
        return template
