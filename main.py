from fastapi import FastAPI, Depends, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
import models, services
from models import SessionLocal, init_db
from contextlib import asynccontextmanager
import re




@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail if isinstance(exc.detail, dict) else {"message": exc.detail}
    )


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
    min_age: int = None,
    max_age: int = None,
    min_gender_probability: float = None,
    min_country_probability: float = None,
    sort_by: str = None,
    order: str = "asc",
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(models.Profile)

    if gender:
        query = query.filter(models.Profile.gender.ilike(gender))
    if country_id:
        query = query.filter(models.Profile.country_id.ilike(country_id))
    if age_group:
        query = query.filter(models.Profile.age_group.ilike(age_group))
    if min_age is not None:
        query = query.filter(models.Profile.age >= min_age)
    if max_age is not None:
        query = query.filter(models.Profile.age <= max_age)
    if min_gender_probability is not None:
        query = query.filter(models.Profile.gender_probability >= min_gender_probability)
    if min_country_probability is not None:
        query = query.filter(models.Profile.country_probability >= min_country_probability)

    total = query.count()

    if not sort_by:
        query = query.order_by(asc(models.Profile.created_at))
    
    if sort_by:
        sort_column = {
            "age": models.Profile.age,
            "created_at": models.Profile.created_at,
            "gender_probability": models.Profile.gender_probability,
        }.get(sort_by)
        if sort_column:
            if order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

    if limit > 50:
        limit = 50
    offset = (page - 1) * limit
    profiles = query.offset(offset).limit(limit).all()

    return {
        "status": "success",
        "page": page,
        "limit": limit,
        "total": total,
        "data": [profile for profile in profiles]
    }

@app.get("/api/profiles/search")
def search_profiles(
    q: str = Query(..., description="Natural language search query"),
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(models.Profile)
    filters = {}
    
    q_lower = q.lower()
    
    if "male" in q_lower or "males" in q_lower:
        filters["gender"] = "male"
    elif "female" in q_lower or "females" in q_lower:
        filters["gender"] = "female"
    
    if "young" in q_lower:
        filters["min_age"] = 16
        filters["max_age"] = 24
    elif "above" in q_lower:
        match = re.search(r"above\s*(\d+)", q_lower)
        if match:
            filters["min_age"] = int(match.group(1))
    elif "below" in q_lower:
        match = re.search(r"below\s*(\d+)", q_lower)
        if match:
            filters["max_age"] = int(match.group(1))
    
    for country_code, country_name in models.COUNTRY_MAP.items():
        if country_name.lower() in q_lower or country_code.lower() in q_lower:
            filters["country_id"] = country_code
            break
    
    for ag in ["child", "teenager", "adult", "senior"]:
        if ag in q_lower:
            filters["age_group"] = ag
            break
    
    if not filters:
        raise HTTPException(status_code=400,
                          detail={"status": "error",
                                   "message": "Unable to interpret query"})
    
    if "gender" in filters:
        query = query.filter(models.Profile.gender.ilike(filters["gender"]))
    if "country_id" in filters:
        query = query.filter(models.Profile.country_id.ilike(filters["country_id"]))
    if "age_group" in filters:
        query = query.filter(models.Profile.age_group.ilike(filters["age_group"]))
    if "min_age" in filters:
        query = query.filter(models.Profile.age >= filters["min_age"])
    if "max_age" in filters:
        query = query.filter(models.Profile.age <= filters["max_age"])
    
    total = query.count()
    
    if limit > 50:
        limit = 50
    offset = (page - 1) * limit
    profiles = query.offset(offset).limit(limit).all()

    return {
        "status": "success",
        "page": page,
        "limit": limit,
        "total": total,
        "data": [profile for profile in profiles]
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