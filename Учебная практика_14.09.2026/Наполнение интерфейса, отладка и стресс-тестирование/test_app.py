"""
Тесты для сервера CRM-интерфейса.
Запуск: python3 test_app.py
Требование: сервер должен быть запущен (python3 server.py)

Покрытие:
  - корректные ответы при нормальной работе
  - автоматический расчёт скидки через discount.py
  - отказоустойчивость (некорректные запросы, недоступные маршруты)
"""

import json
import sys
import os
import unittest
import urllib.request
import urllib.error

# Динамическое связывание: тот же модуль расчёта скидки что использует сервер
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Разработка ядра бизнес-логики (Расчет скидки)"))
from discount import calculate_partner_discount

BASE_URL = "http://localhost:8000"


class TestAPIPartners(unittest.TestCase):
    """Тесты эндпоинта GET /api/partners"""

    @classmethod
    def setUpClass(cls):
        """Загружаем данные один раз для всех тестов"""
        try:
            with urllib.request.urlopen(f"{BASE_URL}/api/partners") as resp:
                cls.partners = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            raise RuntimeError(f"Не удалось подключиться к серверу {BASE_URL}: {e}")

    def test_response_is_list(self):
        """Ответ должен быть списком"""
        self.assertIsInstance(self.partners, list)

    def test_response_not_empty(self):
        """Список партнёров не должен быть пустым"""
        self.assertGreater(len(self.partners), 0)

    def test_partner_has_required_fields(self):
        """Каждый партнёр должен содержать обязательные поля"""
        required = {"partner_id", "company_name", "phone", "rating", "discount_percent"}
        for partner in self.partners:
            for field in required:
                self.assertIn(field, partner, f"Поле '{field}' отсутствует у партнёра {partner}")

    def test_discount_is_integer(self):
        """Скидка должна быть целым числом"""
        for partner in self.partners:
            self.assertIsInstance(partner["discount_percent"], int,
                f"discount_percent не int у {partner['company_name']}")

    def test_discount_valid_values(self):
        """Скидка должна быть одним из допустимых значений: 0, 5, 10, 15"""
        valid = {0, 5, 10, 15}
        for partner in self.partners:
            self.assertIn(partner["discount_percent"], valid,
                f"Недопустимая скидка {partner['discount_percent']} у {partner['company_name']}")

    def test_discount_matches_calculate_function(self):
        """
        Автоматический расчёт: скидка в ответе API должна совпадать
        с результатом функции calculate_partner_discount(total_quantity).
        Проверяет динамическое связывание сервера с модулем discount.
        """
        for partner in self.partners:
            expected = calculate_partner_discount(partner.get("total_quantity", 0))
            self.assertEqual(
                partner["discount_percent"], expected,
                f"Скидка у '{partner['company_name']}' = {partner['discount_percent']}%, "
                f"но calculate_partner_discount({partner.get('total_quantity')}) = {expected}%"
            )

    def test_content_type_json(self):
        """Content-Type должен быть application/json"""
        with urllib.request.urlopen(f"{BASE_URL}/api/partners") as resp:
            ct = resp.headers.get("Content-Type", "")
            self.assertIn("application/json", ct)



class TestFaultTolerance(unittest.TestCase):
    """Тесты на отказоустойчивость"""

    def test_unknown_route_returns_404(self):
        """Несуществующий маршрут должен вернуть 404, а не упасть"""
        try:
            urllib.request.urlopen(f"{BASE_URL}/api/nonexistent")
            self.fail("Ожидался HTTPError 404")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 404)

    def test_unknown_api_route_returns_404(self):
        """Несуществующий API-маршрут должен вернуть 404"""
        try:
            urllib.request.urlopen(f"{BASE_URL}/api/unknown_endpoint")
            self.fail("Ожидался HTTPError 404")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 404)

    def test_multiple_rapid_requests(self):
        """
        Стресс-тест: 20 быстрых запросов подряд — сервер не должен упасть,
        каждый ответ должен быть корректным списком.
        """
        for i in range(20):
            with urllib.request.urlopen(f"{BASE_URL}/api/partners") as resp:
                data = json.loads(resp.read().decode("utf-8"))
                self.assertIsInstance(data, list, f"Запрос {i+1}: ответ не список")

    def test_response_consistent_across_requests(self):
        """Повторные запросы должны возвращать одинаковые данные (стабильность)"""
        with urllib.request.urlopen(f"{BASE_URL}/api/partners") as resp:
            first = json.loads(resp.read().decode("utf-8"))
        with urllib.request.urlopen(f"{BASE_URL}/api/partners") as resp:
            second = json.loads(resp.read().decode("utf-8"))
        self.assertEqual(first, second, "Данные различаются между запросами")


if __name__ == "__main__":
    unittest.main(verbosity=2)
