from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.dependencies import algorithm
from app.routers import members, projects, matching, algorithm as algo_router, utils
from team_matching.data_loader import create_sample_data_from_file
from team_matching.algorithm import TeamMatchingAlgorithm

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global algorithm
    try:
        if os.path.exists(settings.DATA_FILE_PATH):
            algorithm = create_sample_data_from_file(settings.DATA_FILE_PATH)
        else:
            algorithm = TeamMatchingAlgorithm()
        print("Team Matching Algorithm initialized successfully")
    except Exception as e:
        print(f"Warning: Could not load {settings.DATA_FILE_PATH}: {e}")
        algorithm = TeamMatchingAlgorithm()
    
    # Make algorithm available to dependencies
    from app import dependencies
    dependencies.algorithm = algorithm
    
    yield
    
    # Shutdown
    print("Team Matching API shutting down")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
        lifespan=lifespan
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
    )

    # Include routers
    app.include_router(members.router, prefix="/members", tags=["members"])
    app.include_router(projects.router, prefix="/projects", tags=["projects"])
    app.include_router(matching.router, prefix="/projects", tags=["matching"])
    app.include_router(algo_router.router, prefix="/algorithm", tags=["algorithm"])
    app.include_router(utils.router, tags=["utils"])

    @app.get("/")
    async def root():
        """Root endpoint with API information"""
        return {
            "message": settings.API_TITLE,
            "version": settings.API_VERSION,
            "docs": "/docs",
            "status": "active"
        }

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)