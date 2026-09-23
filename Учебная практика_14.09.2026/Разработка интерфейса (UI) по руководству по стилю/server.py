"""
Сервер для CRM-интерфейса партнёров.
Запуск: python3 server.py
Адрес: http://localhost:8000
"""

import json
import os
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

UI_DIR = os.path.join(os.path.dirname(__file__), "..", "Разработка интерфейса (UI)")


def get_partners_with_discounts():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    p.partner_id,
                    p.company_name,
                    p.phone,
                    p.rating,
                    COALESCE(SUM(d.quantity), 0) AS total_quantity,
                    CASE
                        WHEN COALESCE(SUM(d.quantity), 0) >= 300000 THEN 15
                        WHEN COALESCE(SUM(d.quantity), 0) >= 50000  THEN 10
                        WHEN COALESCE(SUM(d.quantity), 0) >= 10000  THEN 5
                        ELSE 0
                    END AS discount_percent
                FROM partners p
                LEFT JOIN deliveries d ON d.partner_id = p.partner_id
                GROUP BY p.partner_id, p.company_name, p.phone, p.rating
                ORDER BY p.partner_id
            """)
            return cur.fetchall()
    finally:
        conn.close()


class CRMHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=UI_DIR, **kwargs)

    def do_GET(self):
        if self.path == "/api/partners":
            try:
                partners = get_partners_with_discounts()
                data = json.dumps([dict(row) for row in partners], ensure_ascii=False)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(data.encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            super().do_GET()

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
