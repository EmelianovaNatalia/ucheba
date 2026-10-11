import sys
import os
import unittest

# Путь к модулю бизнес-логики
sys.path.insert(0, os.path.join(os.path.dirname(__file__),
    "..", "Бизнес-логика (Расчеты и алгоритмы)"))

from business_logic import calculate_materials


class TestCalculateMaterials(unittest.TestCase):

    # Базовый расчёт: 10 × 2.0 × 3.0 × 1.0 × (1 + 0/100) = 60.0 → ceil = 60
    def test_basic_calculation(self):
        result = calculate_materials(1, 1, 10, 2.0, 3.0, 0)
        self.assertEqual(result, 60)

        # Округление строго вверх: 10 × 2.0 × 3.0 × 1.0 × 1.07 = 64.2 → ceil = 65
    def test_ceiling_rounding(self):
        result = calculate_materials(1, 1, 10, 2.0, 3.0, 7)
        self.assertEqual(result, 65)

    # Несуществующий ID типа продукции → -1
    def test_invalid_product_type_id(self):
        result = calculate_materials(9999, 1, 10, 2.0, 3.0, 0)
        self.assertEqual(result, -1)

    # Несуществующий ID материала → -1
    def test_invalid_material_id(self):
        result = calculate_materials(1, 9999, 10, 2.0, 3.0, 0)
        self.assertEqual(result, -1)

    # Отрицательное количество → -1
    def test_negative_quantity(self):
        result = calculate_materials(1, 1, -5, 2.0, 3.0, 0)
        self.assertEqual(result, -1)

    # Отрицательный param1 → -1
    def test_negative_param1(self):
        result = calculate_materials(1, 1, 10, -2.0, 3.0, 0)
        self.assertEqual(result, -1)

    # Отрицательный процент брака → -1
    def test_negative_defect_percent(self):
        result = calculate_materials(1, 1, 10, 2.0, 3.0, -10)
        self.assertEqual(result, -1)


if __name__ == "__main__":
    unittest.main(verbosity=2)