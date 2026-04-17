# Profile Enrichment API (HNG Stage 1)

A high-performance FastAPI backend that aggregates data from multiple external APIs to build enriched user profiles. This project focuses on asynchronous task handling, time-sorted identification using UUID v7, and relational data persistence.

## Features
- **Parallel API Integration**: Uses `httpx` and `asyncio` to fetch data from Genderize, Agify, and Nationalize simultaneously.
- **UUID v7 Implementation**: Generates time-sortable unique identifiers for better database indexing and chronological tracking.
- **Idempotent Endpoints**: Ensures duplicate names do not create redundant database entries.
- **Smart Filtering**: Supports case-insensitive searching by gender, country, and age group.
- **Standardized Error Handling**: Custom 404, 400, and 502 error responses as per HNG requirements.

## 🛠️ Tech Stack
- **Framework**: FastAPI
- **Database**: SQLAlchemy (SQLite for development / PostgreSQL/MySQL ready)
- **HTTP Client**: HTTPX (Asynchronous)
- **Validation**: Pydantic
- **Server**: Uvicorn

## 🏗️ Architecture Flow


1. **Client** sends a POST request with a name.
2. **Server** checks the local database (Idempotency check).
3. If not found, **Async Tasks** are fired in parallel to 3 external APIs.
4. Data is aggregated, categorized (Age Grouping), and persisted.
5. **JSON Response** is returned with a status of 201.

## 📥 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone github.com/echopofi
   cd <project-folder>