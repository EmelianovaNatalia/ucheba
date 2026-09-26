-- ============================================================
-- queries.sql — бизнес-запросы для системы управления партнёрами
-- ============================================================


-- ------------------------------------------------------------
-- 1. Список партнёров с количеством доставок, сортировка по названию
-- ------------------------------------------------------------
SELECT
    p.partner_id,
    p.company_name,
    p.email,
    p.phone,
    p.rating,
    COUNT(d.delivery_id) AS total_deliveries
FROM partners p
LEFT JOIN deliveries d ON p.partner_id = d.partner_id
GROUP BY p.partner_id, p.company_name, p.email, p.phone, p.rating
ORDER BY p.company_name;


-- ------------------------------------------------------------
-- 2. Транзакция: добавление нового партнёра и его первой доставки
-- ------------------------------------------------------------
BEGIN;

INSERT INTO partners (partner_type_id, company_name, inn, director, email, phone, address, rating)
VALUES (1, 'ООО "Новый Партнёр"', '7709876543', 'Иванов И.И.', 'new@partner.ru', '+7 (900) 000-00-00', 'г. Москва, ул. Примерная, д. 1', 0)
ON CONFLICT (inn) DO NOTHING;

INSERT INTO deliveries (partner_id, product_id, quantity, delivery_date)
SELECT partner_id, 1, 10, CURRENT_DATE
FROM partners WHERE inn = '7709876543'
AND NOT EXISTS (
    SELECT 1 FROM deliveries d
    JOIN partners p ON d.partner_id = p.partner_id
    WHERE p.inn = '7709876543' AND d.delivery_date = CURRENT_DATE
);

COMMIT;


-- ------------------------------------------------------------
-- 3. История отгрузок конкретного партнёра за период
-- ------------------------------------------------------------
SELECT
    d.delivery_id,
    p.company_name,
    pr.product_name,
    pr.unit,
    d.quantity,
    pr.min_price,
    ROUND(d.quantity * pr.min_price, 2) AS total_amount,
    d.delivery_date
FROM deliveries d
JOIN partners  p  ON d.partner_id  = p.partner_id
JOIN products  pr ON d.product_id  = pr.product_id
WHERE p.partner_id = 1
  AND d.delivery_date BETWEEN '2026-01-01' AND '2026-12-31'
ORDER BY d.delivery_date;
