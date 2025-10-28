from src.database.base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from .models import TemplateSection, TemplateSectionDependency
from sqlalchemy.future import select

class TemplateSectionRepo(BaseRepository[TemplateSection]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, TemplateSection)
        
    async def get_by_name(self, name: str, template_id: str) -> TemplateSection:
        """
        Retrieve a template section by its name and template ID.
        """
        query = select(self.model).where(
            self.model.name == name,
            self.model.template_id == template_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_order(self, order: int, template_id: str) -> TemplateSection:
        """
        Retrieve a template section by its order and template ID.
        """
        query = select(self.model).where(
            self.model.order == order,
            self.model.template_id == template_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_id(self, section_id: str) -> TemplateSection:
        """
        Retrieve a template section by its ID.
        """
        return await self.session.get(self.model, section_id)   
    
    async def _has_circular_dependency(self, section_id: str, depends_on_id: str) -> bool:
        """
        Verifica si agregar una dependencia crearía una dependencia circular.
        
        Args:
            section_id: ID de la sección que dependerá de otra
            depends_on_id: ID de la sección de la cual dependerá
            
        Returns:
            True si se detecta una dependencia circular, False en caso contrario
        """
        # Si una sección depende de sí misma, es circular
        print(f"Checking circular dependency for section {section_id} depends on {depends_on_id}")
        if str(section_id) == str(depends_on_id):
            return True
        
        # Verificar si depends_on_id ya depende (directa o indirectamente) de section_id
        # Esto detectaría una dependencia circular
        return await self._section_depends_on(depends_on_id, section_id, set())
    
    async def _section_depends_on(self, section_id: str, target_id: str, visited: set) -> bool:
        """
        Verifica recursivamente si section_id depende de target_id.
        
        Args:
            section_id: ID de la sección a verificar
            target_id: ID de la sección objetivo
            visited: Set de IDs ya visitados para evitar bucles infinitos
            
        Returns:
            True si section_id depende de target_id, False en caso contrario
        """
        if section_id in visited:
            return False
        
        visited.add(section_id)
        
        # Obtener todas las dependencias de section_id
        query = select(TemplateSectionDependency).where(
            TemplateSectionDependency.template_section_id == section_id
        )
        result = await self.session.execute(query)
        dependencies = result.scalars().all()
        
        for dependency in dependencies:
            # Si esta sección depende directamente del target, hay dependencia circular
            
            if str(dependency.depends_on_template_section_id) == str(target_id):
                return True
            
            # Verificar recursivamente las dependencias de esta dependencia
            if await self._section_depends_on(dependency.depends_on_template_section_id, target_id, visited.copy()):
                return True
        
        return False
    
    
    async def add(self, section: TemplateSection, dependencies: list[str] = []) -> TemplateSection:
        self.session.add(section)
        await self.session.flush()
        
        # Agregar las dependencias internas
        for depends_on_id in dependencies:
            try:
                await self.add_dependency(section.id, depends_on_id)
            except ValueError as e:
                # Si hay un error al agregar la dependencia, revertir la transacción
                await self.session.rollback()
                raise e
        return section
        
    
    async def add_dependency(self, section_id: str, depends_on_id: str) -> TemplateSectionDependency:
        """
        Add a dependency relationship between two template sections.
        Verifica que no se creen dependencias circulares.
        """
        # Verificar que ambas secciones existan
        section = await self.get_by_id(section_id)
        depends_on_section = await self.get_by_id(depends_on_id)
        
        if not section:
            raise ValueError(f"Section with ID {section_id} not found.")
        if not depends_on_section:
            raise ValueError(f"Section with ID {depends_on_id} not found.")
        
        # Verificar si la dependencia ya existe
        existing_query = select(TemplateSectionDependency).where(
            TemplateSectionDependency.template_section_id == section_id,
            TemplateSectionDependency.depends_on_template_section_id == depends_on_id
        )
        existing_result = await self.session.execute(existing_query)
        existing_dependency = existing_result.scalar_one_or_none()
        
        if existing_dependency:
            raise ValueError(f"Dependency between sections {section_id} and {depends_on_id} already exists.")
        
        # Verificar dependencia circular antes de crear la relación
        if await self._has_circular_dependency(section_id, depends_on_id):
            raise ValueError(
                f"No se puede crear la dependencia: esto generaría una dependencia circular entre las secciones {section_id} y {depends_on_id}"
            )
        
        print(f"Adding dependency from section {section_id} to {depends_on_id}")
        
        # Crear la nueva dependencia
        new_dependency = TemplateSectionDependency(
            template_section_id=section_id,
            depends_on_template_section_id=depends_on_id
        )
        
        self.session.add(new_dependency)
        return new_dependency
    
    async def update_section(self, section: TemplateSection, dependencies: list[str]) -> TemplateSection:
        """
        Update an existing section and its dependencies.
        Verifica que no se creen dependencias circulares al actualizar.
        """
        # Verificar que la sección existe
        existing_section = await self.get_by_id(section.id)
        if not existing_section:
            raise ValueError(f"Section with ID {section.id} not found.")
        
        # Obtener dependencias actuales para poder revertir si hay error
        current_dependencies_query = select(TemplateSectionDependency).where(
            TemplateSectionDependency.template_section_id == section.id
        )
        current_dependencies_result = await self.session.execute(current_dependencies_query)
        current_dependencies = current_dependencies_result.scalars().all()
        
        try:
            # Eliminar todas las dependencias actuales
            for dependency in current_dependencies:
                await self.session.delete(dependency)
            await self.session.flush()
            
            # Verificar cada nueva dependencia antes de agregarla
            for depends_on_id in dependencies:
                # Verificar que la sección objetivo existe
                depends_on_section = await self.get_by_id(depends_on_id)
                if not depends_on_section:
                    raise ValueError(f"Section with ID {depends_on_id} not found.")
                
                # Verificar dependencia circular
                if await self._has_circular_dependency(section.id, depends_on_id):
                    raise ValueError(
                        f"No se puede crear la dependencia: esto generaría una dependencia circular entre las secciones {section.id} y {depends_on_id}"
                    )
            
            # Si todas las verificaciones pasan, agregar las nuevas dependencias
            for depends_on_id in dependencies:
                new_dependency = TemplateSectionDependency(
                    template_section_id=section.id,
                    depends_on_template_section_id=depends_on_id
                )
                self.session.add(new_dependency)
            
            # Actualizar los campos de la sección
            existing_section.name = section.name
            existing_section.type = section.type
            existing_section.prompt = section.prompt
            existing_section.order = section.order
            
            await self.session.flush()
            return existing_section
            
        except Exception as e:
            # Si hay cualquier error, revertir la transacción
            await self.session.rollback()
            raise e