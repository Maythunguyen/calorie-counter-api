from fastapi import UploadFile, File
from fastapi import APIRouter
from app.services.ai_service import AiServices
import json
from fastapi.responses import JSONResponse
from pathlib import Path
from uuid import uuid4
import shutil
import base64

UPLOAD_DIR = Path("app/uploads")

api_router = APIRouter()
@api_router.post("/image_analysis")
async def image_analysis(file: UploadFile = File(...)):
    filename = f"{uuid4()}_{file.filename}"
    saved_path = UPLOAD_DIR / filename
    with saved_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. convert to base64 data-URL
    mime = file.content_type or "image/jpeg"
    data_b64 = base64.b64encode(saved_path.read_bytes()).decode()
    data_url = f"data:{mime};base64,{data_b64}"

    ai_service = AiServices(data_url)
    result = ai_service.image_analysis() 
    return result


    