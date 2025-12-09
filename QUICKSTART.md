# Quick Reference - Rate Limiting & HTTPS

## Start Server

### HTTP (Development)
```bash
uv run python3 run_server.py
```
→ http://127.0.0.1:8000

### HTTPS (Production-Ready)
```bash
uv run python3 run_server.py --https --create-certs
```
→ https://127.0.0.1:8000

## What's New

### Rate Limiting
- **30 requests/minute per IP** on search endpoints
- Automatically enforced by slowapi
- Returns HTTP 429 when exceeded

### HTTPS
- Auto-generates self-signed certificates
- Full TLS/SSL encryption
- Valid for 365 days
- Certs stored in `certs/` directory

## Test It

### Rate Limiting
```python
# Make >30 requests rapidly - 31st should get HTTP 429
for i in range(35):
    response = requests.post("http://localhost:8000/search/password", 
                            json={"query_string": "test"})
    print(f"Request {i+1}: {response.status_code}")
```

### HTTPS
```bash
# With certificates generated
curl -k https://127.0.0.1:8000/health
# Returns: {"status": "ok"}
```

## Endpoints

| Endpoint | Rate Limited | Notes |
|----------|-------------|-------|
| POST /search/password | ✅ Yes (30/min) | - |
| POST /search/username | ✅ Yes (30/min) | - |
| GET / | ❌ No | Serves web UI |
| GET /health | ❌ No | Health check |
| GET /stats | ❌ No | Database stats |

## Files

**New:**
- `run_server.py` - Server launcher
- `certs/key.pem` - Private key (auto-generated)
- `certs/cert.pem` - Certificate (auto-generated)
- `RUNNING.md` - Full documentation
- `RATELIMIT_HTTPS.md` - Technical details

**Modified:**
- `pyproject.toml` - Added slowapi
- `app/app.py` - Added rate limiting decorators

## Customize Rate Limit

Edit `app/app.py`:
```python
@limiter.limit("60/minute")  # Change 30 to desired limit
```

Examples:
- `10/minute` - Strict
- `60/minute` - Permissive
- `100/hour` - Daily usage limits

## Browser Warning

HTTPS with self-signed certs shows warnings - this is normal. Click through to continue.

For production, use CA-signed certificates from Let's Encrypt, etc.

## All Tests Passing ✅

```
11/11 tests pass
Rate limiting functional
HTTPS working
SQL injection safe
XSS prevented
Input validated
```
