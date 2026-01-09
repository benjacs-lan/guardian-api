from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .redis_client import RedisClientManager
from .services.guardian_service import GuardianService
from .config import SessionLocal, settings, engine, Base
from .schemas import CreateGuardian, UpdateGuardian, GuardianResponse

# Configuration Redis
redis_manager = RedisClientManager(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db
)
guardian_service = GuardianService(redis_manager)

# Database dependency
def get_db():
    """Database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(
    title="Guardian API",
    description="Platform Engineering Demo: DevOps Lifecycle",
    version="1.0.0",
)

class DataItem(BaseModel):
    """Request body for data item."""
    key: str
    value: str

@app.get("/health")
async def health_check():
    """Health check endpoint.
    - k8s liveness probe
    - load balancer
    - monitoring
    """
    try:
        redis_status = redis_manager.ping()
        return {
            "status": "healthy",
            "redis": "connected" if redis_status else "disconnected"
        }
    except Exception as e:
        # No fail in the health check for redis,, permission degradation
        return JSONResponse(
            status_code=200,
            content={
                "status": "degraded",
                "redis": "unavailable",
                "message": str(e)
            }
        )
        
@app.post("/data")
async def store_data(item: DataItem):
    try:
        guardian_service.store_data(item.key, item.value)
        return {"status": "success", "data": item}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Internal server error")
    
@app.get("/data/{key}")
async def get_data(key: str):
    try:
        result = guardian_service.get_data(key)
        if result is None:
            raise HTTPException(status_code=404, detail="Service unavailable")
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Internal server error")

@app.on_event("shutdown")
async def shutdown():
    """Shutdown event handler."""
    pass


@app.post("/guardians/", response_model=GuardianResponse)
async def create_guardian(guardian: CreateGuardian, db: Session = Depends(get_db)):
    """
    Create a new guardian.

    - **user_id**: ID of the associated user
    - **ubicacion**: Guardian's location
    - **estado**: Guardian's status
    """
    try:
        db_guardian = guardian_service.create_guardian(db, guardian)
        return GuardianResponse.from_orm(db_guardian)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/guardians/", response_model=list[GuardianResponse])
async def get_guardians(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get list of guardians with pagination.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 10)
    """
    try:
        guardians = guardian_service.get_guardians(db, skip=skip, limit=limit)
        return [GuardianResponse.from_orm(g) for g in guardians]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/guardians/{guardian_id}", response_model=GuardianResponse)
async def get_guardian(guardian_id: int, db: Session = Depends(get_db)):
    try:
        guardian = guardian_service.get_guardian(db, guardian_id)
        if guardian is None:
            raise HTTPException(status_code=404, detail="Guardian not found")
        return GuardianResponse.from_orm(guardian)
    except Exception as e:
        raise HTTPException(status_code=503, detail="Internal server error")

@app.put("/guardians/{guardian_id}", response_model=GuardianResponse)
async def update_guardian(
    guardian_id: int,
    guardian_update: UpdateGuardian,
    db: Session = Depends(get_db)
):
    """
    Update an existing guardian.

    - **guardian_id**: The ID of the guardian to update
    - **ubicacion**: New location (optional)
    - **estado**: New status (optional)
    """
    try:
        db_guardian = guardian_service.update_guardian(db, guardian_id, guardian_update)
        if db_guardian is None:
            raise HTTPException(status_code=404, detail="Guardian not found")
        return GuardianResponse.from_orm(db_guardian)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/guardians/{guardian_id}")
async def delete_guardian(
    guardian_id: int,
    db: Session = Depends(get_db)
):
    try:
        success = guardian_service.delete_guardian(db, guardian_id)
        if not success:
            raise HTTPException(status_code=404, detail="Guardian not found")
        return {"message": "Guardian deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.on_event("startup")
async def create_tables():
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)
