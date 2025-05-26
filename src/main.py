from fastapi import FastAPI
from src.routes.generation import router as generation_router


app = FastAPI()

# Include the generation router
app.include_router(generation_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


