# Profile Query Engine (HNG Stage 2)

A high-performance FastAPI backend that provides advanced query capabilities for profile data. This Stage 2 upgrade adds filtering, sorting, pagination, and natural language query support to the base profile enrichment system.

## Features

### Stage 2 - Query Engine Capabilities

- **Advanced Filtering**: Filter profiles by gender, age_group, country_id, min_age, max_age, min_gender_probability, min_country_probability
- **Sorting**: Sort by age, created_at, or gender_probability (asc/desc)
- **Pagination**: Page and limit parameters with proper envelope response
- **Combined Filters**: All filters work together with AND logic
- **Natural Language Query**: Parse plain English queries to filters
  - "young males" → gender=male + min_age=16 + max_age=24
  - "females above 30" → gender=female + min_age=30
  - "people from Nigeria" → country_id=NG
  - "adult males from Kenya" → gender=male + age_group=adult + country_id=KE

### Stage 1 - Base Features

- **Parallel API Integration**: Uses httpx and asyncio to fetch data from Genderize, Agify, and Nationalize simultaneously
- **UUID v7 Implementation**: Generates time-sortable unique identifiers
- **Idempotent Endpoints**: Duplicate names don't create redundant entries
- **Smart Filtering**: Case-insensitive searching
- **Standardized Error Handling**: Custom 404, 400, 502 error responses

## API Endpoints

### GET /api/profiles

Query profiles with filters, sorting, and pagination.

Query Parameters:
- `gender` - Filter by gender (male/female)
- `country_id` - Filter by country code (NG, KE, etc.)
- `age_group` - Filter by age group (child/teenager/adult/senior)
- `min_age` / `max_age` - Filter by age range
- `min_gender_probability` / `min_country_probability` - Filter by confidence scores
- `sort_by` - Sort by age, created_at, or gender_probability
- `order` - Sort order (asc/desc)
- `page` / `limit` - Pagination (limit max 50)

Example: `/api/profiles?gender=male&country_id=NG&min_age=25&sort_by=age&order=desc`

Response:
```json
{
  "status": "success",
  "page": 1,
  "limit": 10,
  "total": 2317,
  "data": [...]
}
```

### GET /api/profiles/search

Natural language search endpoint.

Query Parameters:
- `q` - Natural language query (required)
- `page` / `limit` - Pagination

Example: `/api/profiles/search?q=young males from nigeria`

### POST /api/profiles

Create a new profile (Stage 1). Data is fetched from external APIs.

### GET /api/profiles/{id}

Get a single profile by ID.

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLAlchemy (SQLite)
- **HTTP Client**: HTTPX
- **Validation**: Pydantic
- **Server**: Uvicorn

## Database

The profiles table contains 2026 seeded records with the following structure:
- id (UUID v7, primary key)
- name (VARCHAR, unique)
- gender (male/female)
- gender_probability (Float)
- age (INT)
- age_group (child/teenager/adult/senior)
- country_id (VARCHAR 2)
- country_name (VARCHAR)
- country_probability (Float)
- created_at (TIMESTAMP)

## Running

```bash
pip install -r requirements.txt
python seed.py  # Seed database with 2026 profiles
uvicorn main:app --host 0.0.0.0 --port 8000
```