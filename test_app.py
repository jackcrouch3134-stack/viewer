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
