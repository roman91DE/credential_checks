import pytest
from fastapi.testclient import TestClient

from app.app import app

# Create a test client
client = TestClient(app)


class TestHealthCheck:
    def test_health_check(self):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestPasswordEndpoint:
    def test_password_partial_match_case_sensitive(self):
        """Test partial password match with case sensitivity"""
        response = client.post(
            "/password",
            json={
                "query_string": "pass",
                "ignore_case": False,
                "include_substring_matches": True,
            },
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)
        # Results should contain passwords with "pass" in them
        if results:
            assert all("pass" in match["matched_string"].lower() for match in results)

    def test_password_partial_match_case_insensitive(self):
        """Test partial password match ignoring case"""
        response = client.post(
            "/password",
            json={
                "query_string": "PASS",
                "ignore_case": True,
                "include_substring_matches": True,
            },
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)
        # Results should contain passwords with "pass" in them (case-insensitive)
        if results:
            assert all("pass" in match["matched_string"].lower() for match in results)

    def test_password_exact_match(self):
        """Test exact password match"""
        response = client.post(
            "/password",
            json={
                "query_string": "password",
                "ignore_case": False,
                "include_substring_matches": False,
            },
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)
        # Results should only contain exact matches
        if results:
            assert all(match["matched_string"] == "password" for match in results)

    def test_password_exact_match_case_insensitive(self):
        """Test exact password match ignoring case"""
        response = client.post(
            "/password",
            json={
                "query_string": "PASSWORD",
                "ignore_case": True,
                "include_substring_matches": False,
            },
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)
        # Results should be exact matches regardless of case
        if results:
            assert all(
                match["matched_string"].lower() == "password" for match in results
            )

    def test_password_no_matches(self):
        """Test password query that returns no results"""
        response = client.post(
            "/password",
            json={
                "query_string": "xyznonexistentpassword123xyz",
                "ignore_case": False,
                "include_substring_matches": True,
            },
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)
        assert len(results) == 0


class TestUsernameEndpoint:
    def test_username_partial_match(self):
        """Test partial username match"""
        response = client.post(
            "/username",
            json={
                "query_string": "user",
                "ignore_case": True,
                "include_substring_matches": True,
            },
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)

    def test_username_exact_match(self):
        """Test exact username match"""
        response = client.post(
            "/username",
            json={
                "query_string": "aaron",
                "ignore_case": False,
                "include_substring_matches": False,
            },
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)
        # Should find "aaron" from names.txt
        if results:
            assert all(match["matched_string"] == "aaron" for match in results)

    def test_username_case_insensitive(self):
        """Test username match with case insensitivity"""
        response = client.post(
            "/username",
            json={
                "query_string": "AARON",
                "ignore_case": True,
                "include_substring_matches": False,
            },
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)
        # Should find "aaron" case-insensitively
        if results:
            assert all(match["matched_string"].lower() == "aaron" for match in results)


class TestStatsEndpoint:
    def test_get_stats(self):
        """Test the stats endpoint"""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_passwords" in data
        assert "sources" in data
        # total_passwords might be a tuple or int depending on implementation
        total = data["total_passwords"]
        if isinstance(total, list):
            total = total[0]
        assert isinstance(total, int)
        assert total > 0
        assert isinstance(data["sources"], list)
        if data["sources"]:
            assert all(
                "name" in source and "count" in source for source in data["sources"]
            )


class TestResponseModel:
    def test_response_structure(self):
        """Test that response matches the expected model"""
        response = client.post(
            "/password",
            json={
                "query_string": "pass",
                "ignore_case": True,
                "include_substring_matches": True,
            },
        )
        assert response.status_code == 200
        results = response.json()

        # Check that each result has the expected fields
        for result in results:
            assert "matched_string" in result
            assert "source" in result
            assert isinstance(result["matched_string"], str)
            assert isinstance(result["source"], str)


# Run with: pytest tests.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
