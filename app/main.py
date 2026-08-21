import logging
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.models import ImproveRequest, ImproveResponse, HealthResponse
from app.services.ai_service import improve_text, AIServiceError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-writing-assistant")

app = FastAPI(title="AI Writing Assistant")

# Serve the frontend files (html/css/js) from /static
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("app/static/index.html")

@app.get("/health", response_model=HealthResponse)
def health_check():
    # Used by Elastic Beanstalk / a load balancer to know the app is alive.
    return {"status": "healthy"}

@app.post("/api/improve", response_model=ImproveResponse)
def improve(request: ImproveRequest):
    try:
        result = improve_text(request.text, request.mode)
    except AIServiceError as e:
        logger.error(f"AI service failed: {e}")
        raise HTTPException(status_code=502, detail="AI service is currently unavailable. Please try again.")
    except Exception as e:
        logger.exception("Unexpected error in /api/improve")
        raise HTTPException(status_code=500, detail="Something went wrong on our end.")

    return {
        "original_text": request.text,
        "mode": request.mode,
        "improved_text": result,
    }