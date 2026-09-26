"""
Сервер CRM-приложения с поддержкой двух экранов.
Запуск: python3 server.py
Адрес: http://localhost:8000

Эндпоинты:
  GET  /api/partners          — список партнеров со скидками
  GET  /api/partner-types     — список типов партнеров для ComboBox
  POST /api/partners/add      — добавление нового партнера (INSERT)
  POST /api/partners/update   — обновление партнера (UPDATE)
"""

import json
import os
import sys

# discount.py лежит в той же папке
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from discount import calculate_partner_discount

from http.server import HTTPServer, SimpleHTTPRequestHandler
import psycopg2
import psycopg2.extras

DB_CONFIG = {
    "dbname": "partners_db",
    "user":   "postgres",
    "password": "",
    "host":   "localhost",
    "port":   5432,
}

UI_DIR = os.path.dirname(__file__)


def db_connect():
    return psycopg2.connect(**DB_CONFIG)


def get_partners():
    conn = db_connect()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT p.partner_id, p.partner_type_id, p.company_name,
                       p.director, p.email, p.phone, p.address, p.inn, p.rating,
                       COALESCE(SUM(d.quantity), 0) AS total_quantity
                FROM partners p
                LEFT JOIN deliveries d ON d.partner_id = p.partner_id
                GROUP BY p.partner_id
                ORDER BY p.partner_id
            """)
            rows = cur.fetchall()
        result = []
        for row in rows:
            partner = dict(row)
            partner["discount_percent"] = calculate_partner_discount(partner["total_quantity"])
            result.append(partner)
        return result
    finally:
        conn.close()


def get_partner_types():
    conn = db_connect()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT partner_type_id, type_name FROM partner_types ORDER BY type_name")
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def add_partner(data):
    """INSERT нового партнера. Проверяем ссылочную целостность: тип должен существовать."""
    conn = db_connect()
    try:
        with conn.cursor() as cur:
            # Проверка ссылочной целостности на уровне приложения
            cur.execute("SELECT 1 FROM partner_types WHERE partner_type_id = %s",
                        (data["partner_type_id"],))
            if not cur.fetchone():
                raise ValueError("Указанный тип партнера не существует в базе данных.")

            cur.execute("""
                INSERT INTO partners
                    (partner_type_id, company_name, director, email, phone, address, inn, rating)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data["partner_type_id"],
                data["company_name"],
                data.get("director", ""),
                data["email"],
                data.get("phone", "Не указан"),
                data.get("address", ""),
                data.get("inn", ""),
                data.get("rating", 0),
            ))
        conn.commit()
    finally:
        conn.close()


def update_partner(data):
    """UPDATE существующего партнера по partner_id."""
    conn = db_connect()
    try:
        with conn.cursor() as cur:
            # Проверка ссылочной целостности на уровне приложения
            cur.execute("SELECT 1 FROM partner_types WHERE partner_type_id = %s",
                        (data["partner_type_id"],))
            if not cur.fetchone():
                raise ValueError("Указанный тип партнера не существует в базе данных.")

            cur.execute("""
                UPDATE partners SET
                    partner_type_id = %s,
                    company_name    = %s,
                    director        = %s,
                    email           = %s,
                    phone           = %s,
                    address         = %s,
                    inn             = %s,
                    rating          = %s
                WHERE partner_id = %s
            """, (
                data["partner_type_id"],
                data["company_name"],
                data.get("director", ""),
                data["email"],
                data.get("phone", "Не указан"),
                data.get("address", ""),
                data.get("inn", ""),
                data.get("rating", 0),
                data["partner_id"],
            ))
        conn.commit()
    finally:
        conn.close()


class CRMHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=UI_DIR, **kwargs)

    def do_GET(self):
        if self.path == "/api/partners":
            self._json_response(get_partners)
        elif self.path == "/api/partner-types":
            self._json_response(get_partner_types)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path in ("/api/partners/add", "/api/partners/update"):
            length = int(self.headers.get("Content-Length", 0))
            body   = self.rfile.read(length)
            try:
                data = json.loads(body)
                if self.path == "/api/partners/add":
                    add_partner(data)
                else:
                    update_partner(data)
                self._send_json(200, {"ok": True})
            except ValueError as e:
                # Ошибки валидации и ссылочной целостности
                self._send_json(400, {"error": str(e)})
            except psycopg2.OperationalError as e:
                self._send_json(503, {"error": f"База данных недоступна: {e}"})
            except psycopg2.Error as e:
                self._send_json(500, {"error": f"Ошибка базы данных: {e}"})
            except Exception as e:
                self._send_json(500, {"error": str(e)})
        else:
            self.send_error(404)

    def _json_response(self, fn):
        """Обёртка для GET-эндпоинтов: вызывает fn(), сериализует результат в JSON."""
        try:
            data = fn()
            self._send_json(200, data)
        except psycopg2.OperationalError as e:
            self._send_json(503, {"error": f"База данных недоступна: {e}"})
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _send_json(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
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
    print("Остановить: Ctrl+C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен.")
