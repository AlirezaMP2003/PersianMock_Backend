# PersianMock Backend

**FastAPI service for generating Persian and Iranian synthetic sample data.**

This repository contains the API, reference-data models, generators, exporters, and backend tests for **PersianMock**. The Vue frontend is maintained in a separate repository.

> **Status:** Portfolio/MVP project. Intended for local development and demonstrations, not for generating verified or guaranteed-unassigned personal identifiers.

## Features

- Schema-driven data generation (1–10,000 rows per request)
- 15 supported field types, including the automatically generated `id`
- Consistent city/province and car company/model relationships
- Unique usernames and emails **within each request**
- JSON, CSV, PostgreSQL-style SQL, and Excel (`.xlsx`) exports
- Optional `CREATE TABLE` statement for SQL exports
- Pydantic request validation and modular exporters

## Supported fields

| Category | Types |
| --- | --- |
| Automatic | `id` (sequential; do not add it as a custom field) |
| Personal | `firstname`, `lastname`, `email`, `username`, `password`, `gender` |
| Location | `province`, `city` |
| Vehicle | `car_company`, `car_name`, `car_color`, `car_year` |
| Identifiers | `mobile_number`, `postal_code` |

`password` produces a **bcrypt hash of a random token**, not a readable password.

## Stack

- Python, FastAPI, Pydantic v2
- SQLAlchemy, PostgreSQL
- Passlib / bcrypt for password hashing
- Pytest, HTTPX, in-memory SQLite for API tests

## Getting started

### Prerequisites

- Python and PostgreSQL installed locally
- A PostgreSQL database created for the project

### Setup (Windows PowerShell)

From the backend repository root:

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root with the database URL expected by `core/config.py`:

```dotenv
DATABASE_URL=postgresql+psycopg2://YOUR_USER:YOUR_PASSWORD@localhost:5432/YOUR_DATABASE
```

Replace every placeholder with your own local values. Do **not** commit `.env`.

The application uses `Base.metadata.create_all()` to create missing tables on startup. It **does not** provide schema migrations. Load the starter reference data with:

```powershell
python -m scripts.seed_reference_data
```

Start the API:

```powershell
python -m uvicorn main:app --reload --port 8001
```

API documentation: <http://127.0.0.1:8001/docs>

> If your backend uses a different Python driver or startup configuration, follow the actual local configuration and update the sample `DATABASE_URL` accordingly.

## API

### `GET /fields/`

Returns the supported generator types.

### `POST /generate/`

Example request:

```json
{
  "table_name": "sample_people",
  "fields": [
    { "type": "firstname", "name": "first_name" },
    { "type": "email", "name": "email" },
    { "type": "city", "name": "city" },
    { "type": "province", "name": "province" }
  ],
  "count": 10,
  "include_create_table": false,
  "format": "json"
}
```

Supported formats: `json`, `csv`, `sql`, `excel`. SQL output may include `CREATE TABLE` when requested. Inspect Swagger for the current response shape.

### Validation and behavior

- Output column names are unique (case-insensitive) and must be valid 1–63-character SQL identifiers.
- `count` must be an integer between 1 and 10,000.
- The `id` column is generated automatically.
- Generated records are **not** saved to the reference tables.

## Reference database

Five PostgreSQL tables support the generator:

| Table | Role |
| --- | --- |
| `first_name` | First names with associated username/email/gender fields |
| `last_name` | Surnames |
| `car` | Paired company and model names |
| `province` | Iranian province names |
| `city` | City names related to provinces |

The starter seed includes 31 provinces, selected cities, and 24 sample car company/model pairs. It is illustrative rather than authoritative or exhaustive.

Algorithmic values include Persian car colors, illustrative Jalali car years (1380–1405), 11-digit `09`-prefixed mobile number strings, and 10-digit postal code strings. Generated phone/postal values may coincide with real assignments.

## Testing

```powershell
python -m pytest -q
```

During MVP development, **29 backend tests were reported passing**. The suite uses in-memory SQLite and does not by itself certify PostgreSQL-specific or production behavior.

## Known limits

- No authentication, accounts, billing, or persistent generated datasets
- No schema migration system
- Preview and export calls generate separate random records
- Request-scale memory use is acceptable for this MVP, but generation is not streamed
- Not intended for real identities or to guarantee unused phone/postal numbers

## Frontend

The separate **PersianMock Frontend** repository contains the Vue application. Run it alongside this service and configure `VITE_API_BASE_URL` to point to the backend.

## License

No license is implied by this README. Add a `LICENSE` file only after choosing the terms under which you want to share this repository.
