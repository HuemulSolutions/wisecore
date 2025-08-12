from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from src.logger import setup_logging
from src.routes.generation_routes import router as generation_router
from src.routes.execution_routes import router as execution_router
from src.routes.document_routes import router as document_router
from src.routes.section_routes import router as section_router
from src.routes.template_routes import router as template_router
from src.routes.organization_routes import router as organization_router

logger = setup_logging()

app = FastAPI()

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
app.include_router(document_router)
app.include_router(template_router)
app.include_router(organization_router)
app.include_router(section_router)

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


