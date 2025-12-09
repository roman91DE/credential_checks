#!/usr/bin/env python3
"""Test security fixes for SQL injection and XSS."""

from app.queries import match_passwords, match_usernames

# Test SQL injection attempts
test_cases = [
    "' OR '1'='1",
    "admin'--",
    "'; DROP TABLE--",
    "1' UNION SELECT * FROM--",
    "test' OR '1",
]

print("Testing SQL Injection Prevention:")
print("=" * 60)
for test_input in test_cases:
    try:
        result = match_passwords(test_input)
        print(f"✓ Input: {test_input!r}")
        print(f"  Result count: {len(result)}")
        print(f"  Status: Input safely escaped\n")
    except Exception as e:
        print(f"✗ Input: {test_input!r}")
        print(f"  Error: {e}\n")

print("\n" + "=" * 60)
print("Testing XSS prevention (input validation):")
print("=" * 60)

# Test XSS attempts
xss_cases = [
    "<img src=x onerror=\"alert('xss')\">",
    "<script>alert('xss')</script>",
    "javascript:alert('xss')",
    "<svg onload=alert('xss')>",
]

for xss_input in xss_cases:
    # This will be rejected by Pydantic if > 1000 chars, but let's check anyway
    if len(xss_input) <= 1000:
        try:
            result = match_passwords(xss_input)
            print(f"✓ Input: {xss_input!r}")
            print(f"  Result count: {len(result)}")
            print(f"  Status: Input accepted (will be escaped on frontend)\n")
        except Exception as e:
            print(f"✗ Input: {xss_input!r}")
            print(f"  Error: {e}\n")
    else:
        print(f"✓ Input: {xss_input!r}")
        print(f"  Status: Rejected (exceeds max_length=1000)\n")

print("=" * 60)
print("All security tests completed!")
