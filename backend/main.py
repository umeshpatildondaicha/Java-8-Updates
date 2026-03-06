from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import upload, jobs, reports
from config import settings

app = FastAPI(
    title="MedViz3D API",
    description="AI-powered medical imaging 3D visualization platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(jobs.router, prefix="/api", tags=["jobs"])
app.include_router(reports.router, prefix="/api", tags=["reports"])

# Serve generated output files (volumes, meshes)
app.mount("/files", StaticFiles(directory=settings.OUTPUT_DIR), name="files")


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0"}
