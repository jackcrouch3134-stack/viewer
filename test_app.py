import unittest

from app import app


class AppRoutesTest(unittest.TestCase):
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

    def test_state_endpoint_contains_agent_payloads(self):
        response = self.client.get("/api/state")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("backend", payload)
        self.assertIn("frontend", payload)
        self.assertIn("ui", payload)
        self.assertEqual(payload["backend"]["status"], "ONLINE")

    def test_compile_endpoint_rejects_empty_code(self):
        response = self.client.post("/api/compile", json={"code": ""})
        self.assertEqual(response.status_code, 400)
        payload = response.get_json()
        self.assertEqual(payload["status"], "error")

    def test_compile_endpoint_accepts_valid_requests(self):
        response = self.client.post("/api/compile", json={"code": "print('hello')"})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["status"], "ok")
        self.assertIn("module_id", payload["result"])

    def test_control_endpoint_rejects_unknown_controls(self):
        response = self.client.post("/api/control", json={"control": "unknown", "value": 1})
        self.assertEqual(response.status_code, 400)
        payload = response.get_json()
        self.assertEqual(payload["status"], "error")

    def test_feedback_endpoint_is_available(self):
        response = self.client.get("/api/feedback")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("feedback", payload)


if __name__ == "__main__":
    unittest.main()
