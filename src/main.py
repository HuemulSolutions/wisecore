from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from src.logger import setup_logging
from src.routes.generation_routes import router as generation_router
from src.routes.execution_routes import router as execution_router
# from src.routes.document_routes import router as document_router
from src.routes.section_routes import router as section_router
# from src.routes.template_routes import router as template_router
# from src.routes.organization_routes import router as organization_router
from src.routes.llm_routes import router as llm_router
from src.routes.chunk_routes import router as chunk_router
from src.routes.doc_type_routes import router as doc_type_router
from src.routes.library_routes import router as library_router
from src.routes.section_execution_routes import router as section_execution_router

from src.modules.templates.routes import router as template_router
from src.modules.template_section.routes import router as template_section_router
from src.modules.organization.routes import router as organization_router
from src.modules.document.routes import router as document_router
from src.database import load_models
from contextlib import asynccontextmanager

logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_models()          # asegúrate de que todos los modelos queden registrados
    yield    

app = FastAPI(lifespan=lifespan)



# Configuración CORS
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include the generation router
app.include_router(generation_router)
app.include_router(execution_router)
app.include_router(document_router, prefix="/api/v1", tags=["Documents"])
app.include_router(template_router, prefix="/api/v1", tags=["Templates"])
app.include_router(template_section_router, prefix="/api/v1", tags=["Template Sections"])
app.include_router(organization_router, prefix="/api/v1", tags=["Organizations"])
app.include_router(section_router)
app.include_router(llm_router)
app.include_router(chunk_router)
app.include_router(doc_type_router)
app.include_router(library_router)
app.include_router(section_execution_router)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(
        f"HTTP {exc.status_code} {request.method} {request.url.path} | detail={exc.detail}",
        exc_info=False
    )
    return JSONResponse(status_code=exc.status_code, content=exc.detail if isinstance(exc.detail, dict) else {"detail": exc.detail})

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error {request.method} {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error"}
    )

@app.get("/")
async def root():
    return {"message": "Hello World"}


