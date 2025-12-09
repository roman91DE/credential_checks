# Credential Checker Web App

A minimalistic web application to check if passwords and usernames have been compromised in known data breaches.

## Features

- 🔍 Search for passwords or usernames
- ✅ Case-insensitive matching (toggle with checkbox)
- 🔤 Substring matching (toggle with checkbox)
- 📊 Scrollable results display with source information
- 🚀 Fast DuckDB backend with parquet data storage

## Running the App

### Start the Server

```bash
uv run app/app.py
```

The app will start on `http://localhost:8000`

### Access the Web Interface

Open your browser and navigate to:
```
http://localhost:8000
```

## How to Use

1. **Enter Search Query**: Type a password or username you want to check
2. **Select Search Type**: Choose between "Password" or "Username" from the dropdown
3. **Configure Matching**:
   - **Ignore Case**: Checked by default for case-insensitive search
   - **Substring Match**: Unchecked by default for exact matches; check to find partial matches
4. **Search**: Click the "Search" button or press Enter
5. **View Results**: Matches appear in the scrollable output field with their breach sources

## API Endpoints

### Web Interface
- `GET /` - Serves the main web interface

### Search Endpoints
- `POST /search/password` - Search for passwords
- `POST /search/username` - Search for usernames

Request body:
```json
{
  "query_string": "search_term",
  "ignore_case": true,
  "include_substring_matches": false
}
```

Response:
```json
[
  {
    "matched_string": "found_value",
    "source": "breach_source.txt"
  }
]
```

### Utility Endpoints
- `GET /health` - Health check
- `GET /stats` - Database statistics

## Data Storage

- Data is stored in parquet format in `data/passwords/` and `data/usernames/`
- The DuckDB database is stored in `database/creads.db`
- The database is automatically created on first run

## Converting Raw Data

If you have raw txt files, use the conversion script:

```bash
uv run convert_to_parquet.py
```

This will convert all txt files to compressed parquet format.

## Testing

Run all tests:
```bash
uv run pytest -v
```
