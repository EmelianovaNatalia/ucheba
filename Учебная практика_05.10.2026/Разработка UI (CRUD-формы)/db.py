import psycopg2


DB_CONFIG = {
    "dbname": "partners_db",
    "user": "mac",
    "host": "localhost",
    "port": 5432,
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def fetch_partners():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.partner_id, pt.type_name, p.partner_name,
                       p.phone, p.rating
                FROM partners p
                JOIN partner_types pt ON pt.partner_type_id = p.partner_type_id
                ORDER BY p.partner_id
            """)
            return cur.fetchall()


def fetch_partner(partner_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT partner_id, partner_type_id, partner_name,
                       inn, email, director, phone, address, rating
                FROM partners
                WHERE partner_id = %s
            """, (partner_id,))
            return cur.fetchone()


def fetch_partner_types():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT partner_type_id, type_name FROM partner_types ORDER BY type_name")
            return cur.fetchall()


def save_partner(data: dict, partner_id: int = None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            if partner_id is None:
                cur.execute("""
                    INSERT INTO partners
                        (partner_type_id, partner_name, inn, email,
                         director, phone, address, rating)
                    VALUES (%(partner_type_id)s, %(partner_name)s, %(inn)s,
                            %(email)s, %(director)s, %(phone)s,
                            %(address)s, %(rating)s)
                """, data)
            else:
                cur.execute("""
                    UPDATE partners SET
                        partner_type_id = %(partner_type_id)s,
                        partner_name    = %(partner_name)s,
                        inn             = %(inn)s,
                        email           = %(email)s,
                        director        = %(director)s,
                        phone           = %(phone)s,
                        address         = %(address)s,
                        rating          = %(rating)s
                    WHERE partner_id = %(partner_id)s
                """, {**data, "partner_id": partner_id})
        conn.commit()


def fetch_sales_history(partner_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT pr.product_name, sh.sale_date, sh.quantity
                FROM sales_history sh
                JOIN products pr ON pr.product_id = sh.product_id
                WHERE sh.partner_id = %s
                ORDER BY sh.sale_date DESC
            """, (partner_id,))
            return cur.fetchall()