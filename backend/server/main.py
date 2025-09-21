from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import uuid
from config.settings import settings
from server.routers.pipeline import router as pipeline_router


app = FastAPI(title="LVX Multi-Agent API")
app.include_router(pipeline_router)

DATA_DIR = Path(settings.DATA_DIR) / "uploads"
DATA_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ingest_pdf")
async def ingest_pdf(files: list[UploadFile] = File(...)):
    saved = []
    for f in files:
        if not f.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        fid = f"{uuid.uuid4()}.pdf"
        dest = DATA_DIR / fid
        with dest.open("wb") as out:
            out.write(await f.read())
        saved.append(str(dest))
    return {"status": "success", "files": saved}
