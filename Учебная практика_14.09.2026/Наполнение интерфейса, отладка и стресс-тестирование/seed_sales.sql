-- Импорт данных о продажах из файла import_sales.txt
-- Данные нормализованы: исправлен формат даты, удалена строка с несуществующим партнёром (partner_id=4)

INSERT INTO deliveries (partner_id, product_id, quantity, delivery_date)
SELECT
    p.partner_id,
    pr.product_id,
    s.quantity,
    s.sale_date::DATE
FROM (VALUES
    (1, 'Стиральный порошок "Альфа"',  '2026-03-01', 50),
    (2, 'Мыло жидкое "Стандарт"',      '2026-03-15', 200),
    (1, 'Кондиционер для белья',        '2026-03-20', 30),
    (3, 'Мыло жидкое "Стандарт"',      '2026-03-25', 150)
) AS s(partner_id, product_name, sale_date, quantity)
JOIN partners p ON p.partner_id = s.partner_id
JOIN products pr ON pr.product_name = s.product_name
ON CONFLICT DO NOTHING;
