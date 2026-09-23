"""
Сервер для CRM-интерфейса партнёров.
Запуск: python3 server.py
Адрес: http://localhost:8000

Автоматический расчёт скидки выполняется функцией calculate_partner_discount
из модуля discount (задание 1), динамически связанной с данными БД.
"""

import json
import os
import sys

# Динамическое связывание: импортируем функцию расчёта скидки из задания 1
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Разработка ядра бизнес-логики (Расчет скидки)"))
from discount import calculate_partner_discount

from http.server import HTTPServer, SimpleHTTPRequestHandler
import psycopg2
import psycopg2.extras

DB_CONFIG = {
    "dbname": "partners_db",
    "user": "postgres",
    "password": "",
    "host": "localhost",
    "port": 5432,
}

UI_DIR = os.path.join(os.path.dirname(__file__), "..", "Разработка интерфейса (UI) по руководству по стилю")


def get_partners_with_discounts():
    """
    Получает партнёров из БД и автоматически рассчитывает скидку
    через функцию calculate_partner_discount (динамическое связывание).
    """
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    p.partner_id,
                    p.company_name,
                    p.phone,
                    p.rating,
                    COALESCE(SUM(d.quantity), 0) AS total_quantity
                FROM partners p
                LEFT JOIN deliveries d ON d.partner_id = p.partner_id
                GROUP BY p.partner_id, p.company_name, p.phone, p.rating
                ORDER BY p.partner_id
            """)
            rows = cur.fetchall()

        result = []
        for row in rows:
            partner = dict(row)
            # Автоматический расчёт скидки через функцию из discount.py
            partner["discount_percent"] = calculate_partner_discount(partner["total_quantity"])
            result.append(partner)
        return result
    finally:
        conn.close()


class CRMHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=UI_DIR, **kwargs)

    def do_GET(self):
        if self.path == "/api/partners":
            try:
                partners = get_partners_with_discounts()
                data = json.dumps(partners, ensure_ascii=False)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(data.encode("utf-8"))
            except psycopg2.OperationalError as e:
                # Отказоустойчивость: БД недоступна — возвращаем понятную ошибку
                self._send_error(503, f"База данных недоступна: {e}")
            except psycopg2.Error as e:
                # Отказоустойчивость: ошибка запроса к БД
                self._send_error(500, f"Ошибка базы данных: {e}")
            except Exception as e:
                # Отказоустойчивость: прочие ошибки сервера
                self._send_error(500, f"Внутренняя ошибка сервера: {e}")
        else:
            super().do_GET()

    def _send_error(self, code, message):
        body = json.dumps({"error": message}, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"[server] {fmt % args}")


if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), CRMHandler)
    print("Сервер запущен: http://localhost:8000")
    print("API партнёров: http://localhost:8000/api/partners")
    print("Остановить: Ctrl+C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен.")
