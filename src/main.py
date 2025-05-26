from fastapi import FastAPI
from src.routes.generation import router as generation_router
from src.routes.execution_routes import router as execution_router


app = FastAPI()

# Include the generation router
app.include_router(generation_router)
app.include_router(execution_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


