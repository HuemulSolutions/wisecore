from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes.generation_routes import router as generation_router
from src.routes.execution_routes import router as execution_router
from src.routes.document_routes import router as document_router
from src.routes.template_routes import router as template_router


app = FastAPI()

# Configuración CORS
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

@app.get("/")
async def root():
    return {"message": "Hello World"}


