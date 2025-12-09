#!/usr/bin/env python3
"""
Run the credential checker server with optional HTTPS support.

Usage:
    python run_server.py                    # Run on HTTP
    python run_server.py --https            # Run on HTTPS (requires certs)
    python run_server.py --https --create   # Create self-signed certs and run on HTTPS
"""

import sys
import argparse
from pathlib import Path
import subprocess
import uvicorn


def create_self_signed_certs(key_file: Path, cert_file: Path) -> bool:
    """Create self-signed certificates using openssl."""
    if key_file.exists() and cert_file.exists():
        print(f"✓ Certificates already exist:")
        print(f"  Key:  {key_file}")
        print(f"  Cert: {cert_file}")
        return True

    print("Creating self-signed certificates...")
    cmd = [
        "openssl", "req", "-x509", "-newkey", "rsa:4096",
        "-keyout", str(key_file),
        "-out", str(cert_file),
        "-days", "365",
        "-nodes",
        "-subj", "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ Certificates created:")
        print(f"  Key:  {key_file}")
        print(f"  Cert: {cert_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error creating certificates: {e}")
        print(f"  Make sure openssl is installed: brew install openssl")
        return False
    except FileNotFoundError:
        print("✗ openssl not found. Install with: brew install openssl")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Run the credential checker server"
    )
    parser.add_argument(
        "--https",
        action="store_true",
        help="Run server on HTTPS instead of HTTP"
    )
    parser.add_argument(
        "--create-certs",
        action="store_true",
        help="Create self-signed certificates if they don't exist"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Server host (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        default=True,
        help="Enable auto-reload on code changes (default: True)"
    )

    args = parser.parse_args()

    # Get the certs directory
    certs_dir = Path(__file__).parent / "certs"

    if args.https:
        certs_dir.mkdir(exist_ok=True)
        key_file = certs_dir / "key.pem"
        cert_file = certs_dir / "cert.pem"

        if args.create_certs or not (key_file.exists() and cert_file.exists()):
            if not create_self_signed_certs(key_file, cert_file):
                sys.exit(1)

        if not (key_file.exists() and cert_file.exists()):
            print("✗ HTTPS certificates not found:")
            print(f"  Key:  {key_file}")
            print(f"  Cert: {cert_file}")
            print("\n  Create them with: python run_server.py --https --create-certs")
            sys.exit(1)

        print(f"\n{'='*60}")
        print("🔒 Starting HTTPS server with rate limiting")
        print(f"{'='*60}")
        print(f"📍 Server: https://{args.host}:{args.port}")
        print(f"⚙️  Rate limit: 30 requests/minute per IP")
        print(f"⚠️  Using self-signed certificate - browser will warn")
        print(f"{'='*60}\n")

        uvicorn.run(
            "app.app:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            ssl_keyfile=str(key_file),
            ssl_certfile=str(cert_file),
        )
    else:
        print(f"\n{'='*60}")
        print("🌐 Starting HTTP server with rate limiting")
        print(f"{'='*60}")
        print(f"📍 Server: http://{args.host}:{args.port}")
        print(f"⚙️  Rate limit: 30 requests/minute per IP")
        print(f"🔒 For HTTPS: python run_server.py --https --create-certs")
        print(f"{'='*60}\n")

        uvicorn.run(
            "app.app:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
        )


if __name__ == "__main__":
    main()
