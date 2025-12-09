# Running the Server

This document explains how to run the credential checker server with HTTP or HTTPS.

## Quick Start

### HTTP (Development)
```bash
uv run python3 run_server.py
```

Server runs on: `http://127.0.0.1:8000`

### HTTPS (Production-Ready with Self-Signed Certificates)
```bash
uv run python3 run_server.py --https --create-certs
```

Server runs on: `https://127.0.0.1:8000`

## Features

### Rate Limiting
- **30 requests per minute** per IP address on all search endpoints
- Automatically enforced by slowapi middleware
- Prevents brute-force attacks and DoS
- Returns HTTP 429 (Too Many Requests) when limit exceeded

### HTTPS Support
- Self-signed certificate generation (development/testing)
- Full TLS/SSL encryption for production deployments
- Certificate files stored in `certs/` directory
- Valid for 365 days after creation

## Command Options

```bash
python3 run_server.py [OPTIONS]
```

### Options:
- `--https` - Enable HTTPS instead of HTTP
- `--create-certs` - Create self-signed certificates if they don't exist
- `--host HOST` - Server host (default: 127.0.0.1)
- `--port PORT` - Server port (default: 8000)
- `--reload` - Enable auto-reload on code changes (default: true)

### Examples:

```bash
# HTTP on default port
uv run python3 run_server.py

# HTTPS on default port with auto-generated certs
uv run python3 run_server.py --https --create-certs

# HTTPS on custom port
uv run python3 run_server.py --https --create-certs --port 9000

# HTTP on all interfaces (0.0.0.0)
uv run python3 run_server.py --host 0.0.0.0

# HTTPS without auto-reload (production)
uv run python3 run_server.py --https --reload=False
```

## Certificate Management

### Auto-Generated Certificates
Self-signed certificates are automatically generated when you run:
```bash
python3 run_server.py --https --create-certs
```

The certificates are stored in:
- **Private Key:** `certs/key.pem`
- **Certificate:** `certs/cert.pem`
- **Valid for:** 365 days

### Using Existing Certificates
If certificates already exist, the server will use them without regenerating.

### Production Certificates
For production, replace the self-signed certificates with certificates from a trusted CA:
1. Obtain certificates from a Certificate Authority (Let's Encrypt, DigiCert, etc.)
2. Replace `certs/key.pem` with your private key
3. Replace `certs/cert.pem` with your certificate

## Rate Limiting Details

### How It Works
- Each IP address gets 30 search requests per minute
- Applies to endpoints: `/search/password`, `/search/username`, `/password`, `/username`
- Limit resets every minute
- Other endpoints (`/health`, `/stats`, `/`) are not rate limited

### Example Response When Rate Limited
```json
{
  "detail": "30 per 1 minute"
}
```

Status Code: `429 Too Many Requests`

### Customizing Rate Limits
To change the rate limit, edit `app/app.py` and modify the decorator:
```python
@limiter.limit("30/minute")  # Change 30 to your desired limit
def search_password(request: Request, query: StringQuery):
    ...
```

Common patterns:
- `10/minute` - 10 per minute
- `100/hour` - 100 per hour
- `1000/day` - 1000 per day

## Browser Warnings with HTTPS

When accessing via HTTPS with self-signed certificates, browsers will show security warnings:

### Chrome/Edge
1. Click "Advanced" or similar button
2. Click "Proceed to localhost (unsafe)" or similar

### Firefox
1. Click "Advanced"
2. Click "Accept Risk and Continue"

### Safari
1. Close the warning dialog
2. Try accessing again, then click "Visit Website"

These warnings are expected for self-signed certificates. In production with a trusted CA certificate, there will be no warnings.

## Monitoring

The server logs all requests:
```
INFO:     127.0.0.1:53241 - "POST /search/password HTTP/1.1" 200 OK
```

To see rate limiting in action:
```bash
# Make >30 requests rapidly to see:
# INFO:     127.0.0.1:12345 - "POST /search/password HTTP/1.1" 429
```

## Troubleshooting

### Certificate Creation Fails
```
✗ openssl not found. Install with: brew install openssl
```

Solution: Install openssl
```bash
brew install openssl
```

### HTTPS Connection Refused
Make sure the port isn't already in use:
```bash
lsof -i :8000
```

If it is, use a different port:
```bash
python3 run_server.py --https --create-certs --port 9000
```

### Rate Limit Too Strict
Adjust in `app/app.py`:
```python
@limiter.limit("60/minute")  # Increase from 30 to 60
```

## API Endpoints

All endpoints are rate-limited to 30 requests/minute:

| Endpoint | Method | Rate Limited |
|----------|--------|--------------|
| `/` | GET | ❌ No |
| `/health` | GET | ❌ No |
| `/stats` | GET | ❌ No |
| `/search/password` | POST | ✅ Yes |
| `/search/username` | POST | ✅ Yes |
| `/password` | POST | ✅ Yes |
| `/username` | POST | ✅ Yes |

## Security Considerations

1. **Self-Signed Certificates** - Fine for development/testing, not for production
2. **Rate Limiting** - Prevents brute-force attacks
3. **Input Validation** - All inputs validated before processing
4. **SQL Injection Prevention** - All queries escaped
5. **XSS Prevention** - All output HTML-escaped

See `SECURITY.md` for more details.
