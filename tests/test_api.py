from unittest import TestCase
from unittest.mock import patch

from app import app
from datetime import datetime, timedelta


class AppTestCase(TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_status(self):
        result = self.app.get("/")
        self.assertEqual(result.status, '200 OK')

    def test_events_without_parameters(self):
        result = self.app.get("/events")
        self.assertEqual(result.status, '400 BAD REQUEST')

