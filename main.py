from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, services
from models import SessionLocal, init_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@app.get("/health")
def health_check():
    return {"status": "Your API is healthy!"}

@app.post("/api/profiles", status_code=201)
async def create_profile(request: dict, db: Session = Depends(get_db)):
    name = request.get("name")

    if not name or not name.strip():
        raise HTTPException(status_code=400, 
                            detail={"status": "error", 
                                     "message": "Missing or empty name"
                                    })
    
    existing_profile = db.query(models.Profile).filter(models.Profile.name.ilike(name)).first()
    if existing_profile:
        return {
            "status": "success",
            "message": "Profile already exists",
            "data": existing_profile
        }
    
    error_api, api_data = await services.fetch_profile_data(name)

    if error_api:
        raise HTTPException(status_code=502, 
                            detail={"status": "error", 
                                     "message": f"{error_api} returned an invalid response"
                                    })
    
    new_profile = models.Profile(name=name, **api_data)
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return {
        "status": "success",
        "data": new_profile
    }

@app.get("/api/profiles")
def get_all_profiles(
    gender: str = None,
    country_id: str = None,
    age_group: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Profile)

    if gender:
        query = query.filter(models.Profile.gender.ilike(gender))
    if country_id:
        query = query.filter(models.Profile.country_id.ilike(country_id))
    if age_group:
        query = query.filter(models.Profile.age_group.ilike(age_group))

    profiles = query.all()

    return {
        "status": "success",
        "count": len(profiles),
        "data": profiles
    }

@app.get("/api/profiles/{profile_id}")
def get_profile(profile_id: str, db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(models.Profile.id == profile_id).first()

    if not profile:
        raise HTTPException(status_code=404, 
                            detail={"status": "error", 
                                     "message": "Profile not found"
                                    })
    
    return {
        "status": "success",
        "data": profile
    }

@app.delete("/api/profiles/{profile_id}", status_code=204)
def delete_profile(profile_id: str, db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(models.Profile.id == profile_id).first()

    if not profile:
        raise HTTPException(status_code=404, 
                            detail={"status": "error", 
                                     "message": "Profile not found"
                                    })
    
    db.delete(profile)
    db.commit()

    return None

@app.delete("/api/profiles/{id}", status_code=204)
def delete_profiles(id: str, db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(models.Profile.id == id).first()

    if not profile:
        raise HTTPException(status_code=404, 
                            detail={"status": "error", 
                                     "message": "Profile not found"
                                    })
    
    db.delete(profile)
    db.commit()

    return None