<<<<<<< HEAD
from app import app


def test_root_assets_are_served_from_static_directory():
    client = app.test_client()

    for path in ["/", "/style.css", "/app.js", "/cartoon.html"]:
        response = client.get(path)
        assert response.status_code == 200, f"{path} should be served successfully"

    static_response = client.get("/static/index.html")
    assert static_response.status_code == 200
    assert b"<html" in static_response.data


def test_api_routes_still_work():
    client = app.test_client()
    response = client.get("/api/compiler/state")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["system_state"]["status"] == "online"
    assert payload["compiled_modules"] == 0
=======
import unittest

from app import app


class AppStaticRoutesTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_root_static_assets_are_served(self):
        for path in ["/style.css", "/app.js"]:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)

    def test_health_endpoint_still_works(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["status"], "healthy")


if __name__ == "__main__":
    unittest.main()
>>>>>>> origin/main
