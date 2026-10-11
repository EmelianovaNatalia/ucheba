import math
import psycopg2


DB_CONFIG = {
    "dbname": "partners_db",
    "user": "mac",
    "host": "localhost",
    "port": 5432,
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def get_discount(partner_id: int) -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COALESCE(SUM(quantity), 0) FROM sales_history WHERE partner_id = %s",
                (partner_id,),
            )
            total = cur.fetchone()[0]
    if total < 10_000:
        return 0
    if total < 50_000:
        return 5
    if total < 300_000:
        return 10
    return 15


def calculate_materials(
    product_type_id: int,
    material_id: int,
    quantity: float,
    param1: float,
    param2: float,
    defect_percent: float,
) -> float:
    if quantity < 0 or param1 < 0 or param2 < 0 or defect_percent < 0:
        return -1
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT type_coefficient FROM product_types WHERE product_type_id = %s",
                (product_type_id,),
            )
            row = cur.fetchone()
            if row is None:
                return -1
            type_coefficient = float(row[0])
            cur.execute(
                "SELECT material_id FROM materials WHERE material_id = %s",
                (material_id,),
            )
            if cur.fetchone() is None:
                return -1
    result = math.ceil(
        quantity * param1 * param2 * type_coefficient * (1 + defect_percent / 100)
    )
    return result