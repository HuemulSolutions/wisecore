from .base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from ..models import Section, Document, SectionExecution, InnerDependency

class SectionRepo(BaseRepository[Section]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Section)
        
    async def get_sections_by_doc_id(self, document_id: str) -> list[Section]:
        
        sections = await self.session.execute(
            select(Section)
            .options(selectinload(Section.internal_dependencies)
                .selectinload(InnerDependency.depends_on_section),)
            .where(Section.document_id == document_id)
            .order_by(Section.order)
        )
        sections = sections.scalars().all()
        
        if sections:
            for section in sections:
                section.dependencies = [dep.depends_on_section.name for dep in section.internal_dependencies]
        else:
            sections = []
            
        return sections
    
    async def get_sections_by_doc_id_graph(self, document_id: str) -> list[Section]:
        sections = await self.session.execute(
            select(Section)
            .options(selectinload(Section.internal_dependencies)
                .selectinload(InnerDependency.depends_on_section))
            .where(Section.document_id == document_id)
            .order_by(Section.order)
        )
        sections = sections.scalars().all()
        
        # Procesar las dependencias para cada sección
        if sections:
            for section in sections:
                # Crear lista de dependencias con id y nombre
                dependencies = [
                    {
                        'id': str(dep.depends_on_section.id),
                        'name': dep.depends_on_section.name
                    }
                    for dep in section.internal_dependencies
                ]
                section.dependencies = dependencies
        else:
            sections = None
        
        return sections
    
    async def get_by_name_and_document_id(self, name: str, document_id: str) -> Section | None:
        result = await self.session.execute(
            select(Section).where(
                Section.name == name,
                Section.document_id == document_id
            )
        )
        return result.scalar_one_or_none()
    
    
    async def get_by_order_and_document_id(self, order: int, document_id: str) -> Section | None:
        result = await self.session.execute(
            select(Section).where(
                Section.order == order,
                Section.document_id == document_id
            )
        )
        return result.scalar_one_or_none()
    
    
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
        query = select(InnerDependency).where(
            InnerDependency.section_id == section_id
        )
        result = await self.session.execute(query)
        dependencies = result.scalars().all()
        
        for dependency in dependencies:
            # Si esta sección depende directamente del target, hay dependencia circular
            
            if str(dependency.depends_on_section_id) == str(target_id):
                return True
            
            # Verificar recursivamente las dependencias de esta dependencia
            if await self._section_depends_on(dependency.depends_on_section_id, target_id, visited.copy()):
                return True
        
        return False
    
    async def add(self, section: Section, dependencies: list[str]) -> Section:
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
    
    async def add_dependency(self, section_id: str, depends_on_id: str) -> InnerDependency:
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
        existing_query = select(InnerDependency).where(
            InnerDependency.section_id == section_id,
            InnerDependency.depends_on_section_id == depends_on_id
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
        new_dependency = InnerDependency(
            section_id=section_id,
            depends_on_section_id=depends_on_id
        )
        
        self.session.add(new_dependency)
        return new_dependency
    
    
        