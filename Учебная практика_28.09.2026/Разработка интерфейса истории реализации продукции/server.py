# server.py
from flask import Flask, jsonify
import psycopg2
import psycopg2.extras

app = Flask(__name__, static_folder=".", static_url_path="")

DB_CONFIG = {
    "dbname": "partners_db",
    "user": "mac",
    "host": "localhost",
    "port": 5432
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/api/partners")
def get_partners():
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT p.partner_id, p.partner_name AS company_name, p.phone, p.rating,
                       0 AS discount_percent
                FROM partners p
                ORDER BY p.partner_name
            """)
            return jsonify(cur.fetchall())
        
@app.route("/api/partners/<int:partner_id>/history")
def get_history(partner_id):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT pr.product_name,
                       sh.quantity,
                       TO_CHAR(sh.sale_date, 'DD.MM.YYYY') AS sale_date
                FROM sales_history sh
                JOIN products pr ON pr.product_id = sh.product_id
                WHERE sh.partner_id = %s
                ORDER BY sh.sale_date DESC
            """, (partner_id,))
            return jsonify(cur.fetchall())

if __name__ == "__main__":
    app.run(debug=True, port=5000)