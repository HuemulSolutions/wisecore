from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.openapi.utils import get_openapi
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from src.logger import setup_logging
from starlette.middleware.base import BaseHTTPMiddleware
from jose import JWTError, jwt
from src.config import system_config

from src.modules.auth.routes import router as auth_router
from src.modules.chatbot.routes import router as chatbot_router
from src.modules.context.routes import router as context_router
from src.modules.document.routes import router as document_router
from src.modules.document_type.routes import router as doc_type_router
from src.modules.docx_template.routes import router as docx_template_router
from src.modules.execution.routes import router as execution_router
from src.modules.folder.routes import router as folder_router
from src.modules.generation.routes import router as generation_router
from src.modules.llm.routes import router as llm_router
from src.modules.llm_provider.routes import router as llm_provider_router
from src.modules.organization.routes import router as organization_router
from src.modules.search.routes import router as search_router
from src.modules.section.routes import router as section_router
from src.modules.section_execution.routes import router as section_execution_router
from src.modules.template.routes import router as template_router
from src.modules.template_section.routes import router as template_section_router

from src.database import load_models
from contextlib import asynccontextmanager

logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_models()
    yield


PUBLIC_PATHS = {
    "/",
    "/openapi.json",
    "/docs",
    "/docs/",
    "/redoc",
    "/api/v1/auth/codes",
    "/api/v1/auth/codes/verify",
    "/api/v1/auth/users",
}

PUBLIC_PREFIXES = (
    "/docs",
    "/redoc",
    "/api/v1/auth/codes",
    "/api/v1/auth/users",
)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Rutas públicas
        if path in PUBLIC_PATHS or path.startswith(PUBLIC_PREFIXES):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse({"detail": "Not authenticated"}, status_code=401)

        token = auth_header[len("Bearer "):]

        try:
            payload = jwt.decode(token, system_config.JWT_SECRET_KEY,
                                 algorithms=[system_config.JWT_ALGORITHM])
        except JWTError:
            return JSONResponse({"detail": "Invalid token"}, status_code=401)

        request.state.jwt_payload = payload
        return await call_next(request)

app = FastAPI(lifespan=lifespan)
app.add_middleware(AuthMiddleware)



# Configuración CORS
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include the routers in alphabetical order
app.include_router(auth_router, prefix="/api/v1", tags=["Auth"])
app.include_router(chatbot_router, prefix="/api/v1", tags=["Chatbot"])
app.include_router(context_router, prefix="/api/v1", tags=["Context"])
app.include_router(document_router, prefix="/api/v1", tags=["Documents"])
app.include_router(doc_type_router, prefix="/api/v1", tags=["Document Types"])
app.include_router(docx_template_router, prefix="/api/v1", tags=["Docx Templates"])
app.include_router(execution_router, prefix="/api/v1", tags=["Executions"])
app.include_router(folder_router, prefix="/api/v1", tags=["Folders"])
app.include_router(generation_router, prefix="/api/v1", tags=["Generation"])
app.include_router(llm_router, prefix="/api/v1", tags=["LLMs"])
app.include_router(llm_provider_router, prefix="/api/v1", tags=["LLM Providers"])
app.include_router(organization_router, prefix="/api/v1", tags=["Organizations"])
app.include_router(search_router, prefix="/api/v1", tags=["Search"])
app.include_router(section_router, prefix="/api/v1", tags=["Sections"])
app.include_router(section_execution_router, prefix="/api/v1", tags=["Section Executions"])
app.include_router(template_router, prefix="/api/v1", tags=["Templates"])
app.include_router(template_section_router, prefix="/api/v1", tags=["Template Sections"])


def custom_openapi():
    """
    Expose bearer auth in Swagger UI so the Authorize button appears.
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Wisecore API",
        version="1.0.0",
        description="Wisecore service API",
        routes=app.routes,
    )

    security_scheme = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {}).update(security_scheme)
    openapi_schema.setdefault("security", []).append({"bearerAuth": []})

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

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
