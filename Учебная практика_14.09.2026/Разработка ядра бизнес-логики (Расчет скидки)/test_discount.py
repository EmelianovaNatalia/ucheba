"""
Юнит-тесты для функции calculate_partner_discount.
Запуск: python3 test_discount.py
"""

import unittest
from discount import calculate_partner_discount


class TestCalculatePartnerDiscount(unittest.TestCase):

    def test_zero_quantity(self):
        """Ноль единиц — скидка 0%"""
        self.assertEqual(calculate_partner_discount(0), 0)

    def test_below_threshold_10000(self):
        """Меньше 10 000 — скидка 0%"""
        self.assertEqual(calculate_partner_discount(9999), 0)

    def test_exactly_10000(self):
        """Ровно 10 000 — скидка 5%"""
        self.assertEqual(calculate_partner_discount(10000), 5)

    def test_between_10000_and_50000(self):
        """49 999 единиц — скидка 5%"""
        self.assertEqual(calculate_partner_discount(49999), 5)

    def test_exactly_50000(self):
        """Ровно 50 000 — скидка 10%"""
        self.assertEqual(calculate_partner_discount(50000), 10)

    def test_between_50000_and_300000(self):
        """299 999 единиц — скидка 10%"""
        self.assertEqual(calculate_partner_discount(299999), 10)

    def test_exactly_300000(self):
        """Ровно 300 000 — скидка 15%"""
        self.assertEqual(calculate_partner_discount(300000), 15)

    def test_above_300000(self):
        """Выше максимума — скидка 15%"""
        self.assertEqual(calculate_partner_discount(500000), 15)


if __name__ == "__main__":
    unittest.main(verbosity=2)
