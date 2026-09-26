"""
Тесты для CRM-сервера с поддержкой CRUD-операций.
Запуск: python3 test_app.py
Требование: сервер должен быть запущен на http://localhost:8000
"""

import json
import unittest
import urllib.request
import urllib.error

BASE = "http://localhost:8000"


class TestAPIPartners(unittest.TestCase):
    """Тесты GET /api/partners"""

    def test_response_is_list(self):
        """Ответ /api/partners должен быть JSON-массивом"""
        with urllib.request.urlopen(f"{BASE}/api/partners") as resp:
            data = json.load(resp)
        self.assertIsInstance(data, list)

    def test_required_fields(self):
        """Каждый партнер содержит обязательные поля"""
        with urllib.request.urlopen(f"{BASE}/api/partners") as resp:
            partners = json.load(resp)
        if not partners:
            self.skipTest("Нет партнеров в БД")
        required = {"partner_id", "company_name", "email", "rating", "discount_percent"}
        for p in partners:
            for field in required:
                self.assertIn(field, p, f"Поле '{field}' отсутствует")

    def test_discount_is_integer(self):
        """discount_percent должен быть целым числом"""
        with urllib.request.urlopen(f"{BASE}/api/partners") as resp:
            partners = json.load(resp)
        for p in partners:
            self.assertIsInstance(p["discount_percent"], int)

    def test_discount_valid_values(self):
        """discount_percent должен быть одним из: 0, 5, 10, 15"""
        with urllib.request.urlopen(f"{BASE}/api/partners") as resp:
            partners = json.load(resp)
        for p in partners:
            self.assertIn(p["discount_percent"], {0, 5, 10, 15})

    def test_content_type_json(self):
        """Content-Type должен содержать application/json"""
        with urllib.request.urlopen(f"{BASE}/api/partners") as resp:
            ct = resp.headers.get("Content-Type", "")
        self.assertIn("application/json", ct)

    def test_discount_matches_calculate_function(self):
        """discount_percent должен совпадать с результатом calculate_partner_discount"""
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from discount import calculate_partner_discount

        with urllib.request.urlopen(f"{BASE}/api/partners") as resp:
            partners = json.load(resp)
        for p in partners:
            expected = calculate_partner_discount(p.get("total_quantity", 0))
            self.assertEqual(p["discount_percent"], expected,
                f"Партнёр {p['partner_id']}: ожидалось {expected}%, получено {p['discount_percent']}%")


class TestAPIPartnerTypes(unittest.TestCase):
    """Тесты GET /api/partner-types"""

    def test_response_is_list(self):
        with urllib.request.urlopen(f"{BASE}/api/partner-types") as resp:
            data = json.load(resp)
        self.assertIsInstance(data, list)

    def test_required_fields(self):
        with urllib.request.urlopen(f"{BASE}/api/partner-types") as resp:
            types = json.load(resp)
        if not types:
            self.skipTest("Нет типов партнеров в БД")
        for t in types:
            self.assertIn("partner_type_id", t)
            self.assertIn("type_name", t)


class TestCRUDAdd(unittest.TestCase):
    """Тесты POST /api/partners/add"""

    def _post(self, url, data):
        body = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(
            url, data=body,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.load(resp)
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def _get_first_type_id(self):
        with urllib.request.urlopen(f"{BASE}/api/partner-types") as resp:
            types = json.load(resp)
        if not types:
            self.skipTest("Нет типов партнеров в БД")
        return types[0]["partner_type_id"]

    def test_add_valid_partner(self):
        """Добавление партнера с корректными данными → 200"""
        type_id = self._get_first_type_id()
        status, result = self._post(f"{BASE}/api/partners/add", {
            "partner_type_id": type_id,
            "company_name": "ООО ТестКомпания",
            "director": "Тестов Тест Тестович",
            "email": "test_crud@test.ru",
            "phone": "+7 (999) 000-00-00",
            "address": "г. Тест, ул. Тестовая, 1",
            "inn": "1234509876",
            "rating": 5,
        })
        self.assertEqual(status, 200)
        self.assertTrue(result.get("ok"))

    def test_add_invalid_type(self):
        """Добавление с несуществующим типом → 400"""
        status, result = self._post(f"{BASE}/api/partners/add", {
            "partner_type_id": 999999,
            "company_name": "ООО Ошибка",
            "email": "err@err.ru",
        })
        self.assertEqual(status, 400)
        self.assertIn("error", result)


class TestFaultTolerance(unittest.TestCase):
    """Тесты отказоустойчивости"""

    def test_unknown_route_404(self):
        """Неизвестный маршрут → 404"""
        try:
            urllib.request.urlopen(f"{BASE}/api/nonexistent")
            self.fail("Ожидался HTTPError 404")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 404)

    def test_multiple_rapid_requests(self):
        """20 последовательных запросов → все 200"""
        for i in range(20):
            with urllib.request.urlopen(f"{BASE}/api/partners") as resp:
                self.assertEqual(resp.status, 200, f"Запрос {i+1} вернул не 200")

    def test_response_consistent(self):
        """Два запроса подряд возвращают одинаковое количество записей"""
        with urllib.request.urlopen(f"{BASE}/api/partners") as r1:
            count1 = len(json.load(r1))
        with urllib.request.urlopen(f"{BASE}/api/partners") as r2:
            count2 = len(json.load(r2))
        self.assertEqual(count1, count2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
