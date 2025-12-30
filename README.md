# Issue Tracker API

A robust backend service built with **FastAPI** and **PostgreSQL** for managing issues, comments, and labels. This project demonstrates real-world patterns including optimistic concurrency control, transactional updates, and CSV data imports.

## Features

- **Issue Management**: Create, read, update, and delete issues.
- **Optimistic Concurrency**: Version-based locking to prevent lost updates.
- **Comments**: Add comments to issues with author validation.
- **Labels**: Categorize issues with atomic label updates.
- **Bulk Operations**: Transactional bulk status updates.
- **Data Import**: Upload CSV files to bulk create issues with validation.
- **Analytics**: Reports for top assignees and issue resolution latency.

## Prerequisites

- **Python 3.8+**
- **PostgreSQL**: Ensure you have a running PostgreSQL instance.

## Installation

1.  **Clone the repository** (if applicable) or navigate to the project directory.

2.  **Create a virtual environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The database connection is configured in `app/database.py`.
By default, it connects to:
`postgresql://postgres:password@localhost:5434/postgres`

**Important**: Ensure your PostgreSQL server is running on port **5434** and the password matches. You can modify `app/database.py` to change these settings.

## Running the Application

Start the development server with hot-reload enabled:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Documentation

Interactive API documentation (Swagger UI) is automatically generated and available at:

👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

You can use this interface to test all endpoints directly from your browser.

## Testing

A verification script `test_api.py` is included to test core functionalities.

```bash
python test_api.py
```

## Project Structure

```
├── app/
│   ├── main.py          # API Endpoints and application entry point
│   ├── models.py        # SQLAlchemy database models
│   ├── schemas.py       # Pydantic models for request/response validation
│   ├── crud.py          # Database CRUD operations
│   ├── database.py      # Database connection and session setup
│   └── dependencies.py  # Dependency injection (e.g., DB session)
├── requirements.txt     # Python dependencies
├── check_db.py          # Script to verify database connection
└── test_api.py          # API verification script
```
