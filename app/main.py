from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.image_analysis import api_router


app = FastAPI(
    title="Calories calculator App",
    description="Backend for calories calculattion with OpenAI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to the Calcal Service!"}


app.include_router(api_router, prefix="/api", tags=["api"])