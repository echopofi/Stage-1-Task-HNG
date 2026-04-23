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
    db = SessionLocal()
    existing = db.query(models.Profile).count()
    if existing < 2026:
        import random
        from uuid6 import uuid7
        from models import COUNTRY_MAP
        
        MALE_FIRST_NAMES = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles", "Christopher", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua", "Kenneth", "Kevin", "Brian", "George"]
        FEMALE_FIRST_NAMES = ["Mary", "Jennifer", "Linda", "Patricia", "Barbara", "Susan", "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra", "Ashley", "Kimberly", "Emily", "Donna", "Michelle", "Dorothy", "Carol", "Amanda", "Melissa", "Deborah"]
        LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
        
        def get_age_group(age):
            if age <= 12: return "child"
            elif age <= 19: return "teenager"
            elif age <= 59: return "adult"
            else: return "senior"
        
        country_ids = list(COUNTRY_MAP.keys())
        all_names = {p[0] for p in db.query(models.Profile.name).all()}
        profiles_to_add = []
        
        while len(profiles_to_add) + existing < 2026:
            gender = random.choice(["male", "female"])
            first = random.choice(MALE_FIRST_NAMES if gender == "male" else FEMALE_FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            suffix = random.randint(1, 9999)
            name = f"{first} {last} {suffix}"
            
            if name in all_names:
                all_names.add(name)
                continue
            
            all_names.add(name)
            age = random.randint(1, 85)
            country_id = random.choice(country_ids)
            
            profile = models.Profile(
                id=str(uuid7()),
                name=name,
                gender=gender,
                gender_probability=round(random.uniform(0.5, 1.0), 2),
                age=age,
                age_group=get_age_group(age),
                country_id=country_id,
                country_name=COUNTRY_MAP.get(country_id, country_id),
                country_probability=round(random.uniform(0.1, 0.9), 2)
            )
            profiles_to_add.append(profile)
            
            if len(profiles_to_add) >= 100:
                db.bulk_save_objects(profiles_to_add)
                db.commit()
                profiles_to_add = []
        
        if profiles_to_add:
            db.bulk_save_objects(profiles_to_add)
            db.commit()
    
    db.close()
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

@app.post("/api/seed")
def seed_database(db: Session = Depends(get_db)):
    import random
    from uuid6 import uuid7
    from models import COUNTRY_MAP
    
    existing = db.query(models.Profile).count()
    if existing >= 2026:
        return {"status": "success", "message": f"Database already has {existing} profiles"}
    
    MALE_FIRST_NAMES = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles", "Christopher", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua", "Kenneth", "Kevin", "Brian", "George"]
    FEMALE_FIRST_NAMES = ["Mary", "Jennifer", "Linda", "Patricia", "Barbara", "Susan", "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra", "Ashley", "Kimberly", "Emily", "Donna", "Michelle", "Dorothy", "Carol", "Amanda", "Melissa", "Deborah"]
    LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
    
    def get_age_group(age):
        if age <= 12: return "child"
        elif age <= 19: return "teenager"
        elif age <= 59: return "adult"
        else: return "senior"
    
    country_ids = list(COUNTRY_MAP.keys())
    created = 0
    profiles_to_add = []
    
    all_names = {p[0] for p in db.query(models.Profile.name).all()}
    
    while created < 2026:
        gender = random.choice(["male", "female"])
        first = random.choice(MALE_FIRST_NAMES if gender == "male" else FEMALE_FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        suffix = random.randint(1, 9999)
        name = f"{first} {last} {suffix}"
        
        if name in all_names:
            all_names.add(name)
            continue
        
        all_names.add(name)
        age = random.randint(1, 85)
        country_id = random.choice(country_ids)
        
        profile = models.Profile(
            id=str(uuid7()),
            name=name,
            gender=gender,
            gender_probability=round(random.uniform(0.5, 1.0), 2),
            age=age,
            age_group=get_age_group(age),
            country_id=country_id,
            country_name=COUNTRY_MAP.get(country_id, country_id),
            country_probability=round(random.uniform(0.1, 0.9), 2)
        )
        profiles_to_add.append(profile)
        created += 1
        all_names.add(name)
        
        if len(profiles_to_add) >= 100:
            db.bulk_save_objects(profiles_to_add)
            db.commit()
            profiles_to_add = []
    
    if profiles_to_add:
        db.bulk_save_objects(profiles_to_add)
        db.commit()
    
    final_count = db.query(models.Profile).count()
    return {"status": "success", "message": f"Seeded database with {final_count} profiles"}

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
        valid_sort_fields = {"age", "created_at", "gender_probability"}
        if sort_by not in valid_sort_fields:
            raise HTTPException(status_code=400,
                              detail={"status": "error",
                                       "message": "Invalid query parameters"})
        sort_column = {
            "age": models.Profile.age,
            "created_at": models.Profile.created_at,
            "gender_probability": models.Profile.gender_probability,
        }.get(sort_by)
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
    if not q or not q.strip():
        raise HTTPException(status_code=400,
                          detail={"status": "error",
                                   "message": "Invalid query parameters"})
    
    query = db.query(models.Profile)
    filters = {}
    
    q_lower = q.lower()
    
    gender_filter_applied = False
    if ("male" in q_lower or "males" in q_lower) and ("female" in q_lower or "females" in q_lower):
        gender_filter_applied = False
    elif "male" in q_lower or "males" in q_lower:
        filters["gender"] = "male"
        gender_filter_applied = True
    elif "female" in q_lower or "females" in q_lower:
        filters["gender"] = "female"
        gender_filter_applied = True
    
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
    
    query_words = set(q_lower.replace(",", " ").replace("from", " ").replace("of", " ").split())
    
    for country_code, country_name in models.COUNTRY_MAP.items():
        if country_code.lower() in query_words or country_name.lower() in query_words:
            filters["country_id"] = country_code
            break
    
    for ag in ["child", "teenager", "adult", "senior"]:
        if ag in query_words:
            filters["age_group"] = ag
            break
    
    valid_keywords = set()
    valid_keywords.update(["male", "males", "female", "females", "young", "above", "below", "child", "teenager", "adult", "senior"])
    valid_keywords.update([c.lower() for c in models.COUNTRY_MAP.keys()])
    valid_keywords.update([n.lower() for n in models.COUNTRY_MAP.values()])
    
    if not filters or not query_words.intersection(valid_keywords):
        raise HTTPException(status_code=400,
                          detail={"status": "error",
                                   "message": "Unable to interpret query"})
    
    if "gender" in filters and filters["gender"] is not None:
        query = query.filter(models.Profile.gender == filters["gender"])
    if "gender" in filters and filters["gender"] is None:
        pass
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