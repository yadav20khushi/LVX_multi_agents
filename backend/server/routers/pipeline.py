from fastapi import APIRouter, HTTPException
from pathlib import Path

router = APIRouter(prefix="/pipeline")

@router.post("/run")
def run_pipeline(files: list[str]):
    for f in files:
        if not Path(f).exists():
            raise HTTPException(status_code=400, detail=f"File not found: {f}")

    return {
        "status": "ok",
        "hint": "Paste these into the ADK Dev UI message as {'files': [...]} to trigger A1→A3.",
        "files": files,
    }
