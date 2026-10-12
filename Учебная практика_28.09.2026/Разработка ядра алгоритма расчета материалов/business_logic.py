# business_logic.py
# Задание 2: Разработка ядра алгоритма расчета материалов

import math
import psycopg2

DB_CONFIG = {
    "dbname": "partners_db",
    "user": "mac",
    "host": "localhost",
    "port": 5432
}

# Мок-данные процента брака по типу материала (т.к. в БД нет этой колонки)
MATERIAL_DEFECT = {
    1: 5.0,
    2: 3.0,
    3: 8.0,
    4: 2.5,
    5: 10.0,
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def calculate_materials(product_type_id, material_type_id, quantity, param_1, param_2):
    # Валидация входных параметров
    if quantity <= 0 or param_1 < 0 or param_2 < 0:
        return -1

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Получаем коэффициент типа продукции из БД
                cur.execute(
                    "SELECT type_coefficient FROM product_types WHERE product_type_id = %s",
                    (product_type_id,)
                )
                row = cur.fetchone()
                if row is None:
                    return -1
                type_coefficient = float(row[0])

        # Получаем процент брака из мок-данных
        defect_percent = MATERIAL_DEFECT.get(material_type_id)
        if defect_percent is None:
            return -1

        # Базовый расход на 1 единицу продукции
        base_per_unit = param_1 * param_2 * type_coefficient

        # Общий чистый расход
        total_clean = base_per_unit * quantity

        # Итоговый расход с учётом брака
        total_with_defect = total_clean * (1 + defect_percent / 100)

        # Округление вверх до целого
        return math.ceil(total_with_defect)

    except Exception:
        return -1