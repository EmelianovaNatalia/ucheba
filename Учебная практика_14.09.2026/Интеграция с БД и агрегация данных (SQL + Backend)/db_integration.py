import psycopg2


# Настройки подключения к БД
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "partners_db",
    "user": "postgres",
    "password": "your_password",
}


def calculate_partner_discount(total_quantity: int) -> int:
    if total_quantity >= 300000:
        return 15
    if total_quantity >= 50000:
        return 10
    if total_quantity >= 10000:
        return 5
    return 0


def get_partner_with_discount(partner_id: int) -> dict | None:
    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            p.partner_id,
            p.company_name,
            p.email,
            p.phone,
            p.rating,
            COALESCE(SUM(d.quantity), 0) AS total_quantity
        FROM partners p
        LEFT JOIN deliveries d ON p.partner_id = d.partner_id
        WHERE p.partner_id = %s
        GROUP BY p.partner_id, p.company_name, p.email, p.phone, p.rating
        """,
        (partner_id,)
    )

    row = cursor.fetchone()
    cursor.close()
    connection.close()

    if row is None:
        return None

    total_quantity = int(row[5])
    discount = calculate_partner_discount(total_quantity)

    partner = {
        "partner_id":    row[0],
        "company_name":  row[1],
        "email":         row[2],
        "phone":         row[3],
        "rating":        row[4],
        "total_quantity": total_quantity,
        "discount":      discount,
    }

    return partner


def get_all_partners_with_discounts() -> list[dict]:
    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            p.partner_id,
            p.company_name,
            p.email,
            p.phone,
            p.rating,
            COALESCE(SUM(d.quantity), 0) AS total_quantity
        FROM partners p
        LEFT JOIN deliveries d ON p.partner_id = d.partner_id
        GROUP BY p.partner_id, p.company_name, p.email, p.phone, p.rating
        ORDER BY p.company_name
        """
    )

    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    partners = []
    for row in rows:
        total_quantity = int(row[5])
        discount = calculate_partner_discount(total_quantity)
        partner = {
            "partner_id":     row[0],
            "company_name":   row[1],
            "email":          row[2],
            "phone":          row[3],
            "rating":         row[4],
            "total_quantity": total_quantity,
            "discount":       discount,
        }
        partners.append(partner)

    return partners


if __name__ == "__main__":
    print("=== Один партнёр (partner_id=1) ===")
    partner = get_partner_with_discount(1)
    if partner:
        for key, value in partner.items():
            print(f"  {key}: {value}")
    else:
        print("  Партнёр не найден")

    print("\n=== Все партнёры со скидками ===")
    all_partners = get_all_partners_with_discounts()
    for p in all_partners:
        print(f"  {p['company_name']}: объём={p['total_quantity']} ед., скидка={p['discount']}%")
