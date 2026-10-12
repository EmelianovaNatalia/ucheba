# test_business_logic.py
# Задание 4: Модульное тестирование и аудит безопасности

import sys
import unittest

sys.path.append("../Разработка ядра алгоритма расчета материалов")
from business_logic import calculate_materials

class TestCalculateMaterials(unittest.TestCase):

    # Тест 1: Стандартный корректный расчёт
    # product_type_id=1 (coefficient=1.0), material_type_id=1 (defect=5%)
    # 10 * 2.0 * 3.0 * 1.0 * 1.05 = 63.0 → ceil = 63
    def test_standard(self):
        result = calculate_materials(1, 1, 10, 2.0, 3.0)
        self.assertEqual(result, 63)

    # Тест 2: Округление вверх (ceil)
    # 10 * 2.0 * 3.0 * 1.0 * 1.05 = 63.0, но с param_1=2.1:
    # 10 * 2.1 * 3.0 * 1.0 * 1.05 = 66.15 → ceil = 67
    def test_ceiling(self):
        result = calculate_materials(1, 1, 10, 2.1, 3.0)
        self.assertEqual(result, 67)

    # Тест 3: Несуществующий тип продукции → -1
    def test_invalid_product_type(self):
        result = calculate_materials(9999, 1, 10, 2.0, 3.0)
        self.assertEqual(result, -1)

    # Тест 4: Несуществующий тип материала → -1
    def test_invalid_material_type(self):
        result = calculate_materials(1, 9999, 10, 2.0, 3.0)
        self.assertEqual(result, -1)

    # Тест 5: Отрицательный param_1 → -1
    def test_negative_param1(self):
        result = calculate_materials(1, 1, 10, -2.0, 3.0)
        self.assertEqual(result, -1)

    # Тест 6: Отрицательный param_2 → -1
    def test_negative_param2(self):
        result = calculate_materials(1, 1, 10, 2.0, -3.0)
        self.assertEqual(result, -1)

    # Тест 7: Количество равно 0 → -1
    def test_zero_quantity(self):
        result = calculate_materials(1, 1, 0, 2.0, 3.0)
        self.assertEqual(result, -1)

if __name__ == "__main__":
    unittest.main()
