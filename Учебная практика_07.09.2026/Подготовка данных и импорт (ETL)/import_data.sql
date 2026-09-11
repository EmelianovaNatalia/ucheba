-- ============================================================
-- import_data.sql — очищенные данные для импорта
-- Аномалии исправлены:
--   partners: NULL phone → 'Не указан', NULL rating → 0, лишние пробелы
--   sales: дата 15.03.2026 → 2026-03-15, удалена строка с partner_id=4 (не существует)
-- ============================================================

-- Справочники (минимальные данные)
INSERT INTO partner_types (partner_type_id, type_name) VALUES
    (1, 'ООО'),
    (2, 'ИП'),
    (3, 'ТК')
ON CONFLICT (partner_type_id) DO NOTHING;

INSERT INTO product_types (product_type_id, type_name) VALUES
    (1, 'Бытовая химия')
ON CONFLICT (product_type_id) DO NOTHING;

INSERT INTO products (product_id, product_type_id, product_name, article, unit, min_price) VALUES
    (1, 1, 'Стиральный порошок "Альфа"', 'ART-001', 'шт.', 0.00),
    (2, 1, 'Мыло жидкое "Стандарт"', 'ART-002', 'шт.', 0.00),
    (3, 1, 'Кондиционер для белья', 'ART-003', 'шт.', 0.00)
ON CONFLICT (product_id) DO NOTHING;

INSERT INTO partners (partner_id, partner_type_id, company_name, inn, director, email, phone, address, rating) VALUES
    (1, 1, 'ООО "Логистик-Экспресс"', '7701234567', 'Не указан', 'info@logex.ru', '+7 (999) 111-22-33', 'Не указан', 4.8),
    (2, 2, 'ИП Петров А.В.', '5001098765', 'Не указан', 'petrov_delivery@mail.ru', 'Не указан', 'Не указан', 4.2),
    (3, 3, 'ТК "Быстрый Путь"', '7812345678', 'Не указан', 'speedway@yandex.ru', '+78125554433', 'Не указан', 0.0)
ON CONFLICT (partner_id) DO NOTHING;

INSERT INTO deliveries (delivery_id, partner_id, product_id, quantity, delivery_date) VALUES
    (101, 1, 1, 50, '2026-03-01'),
    (102, 2, 2, 200, '2026-03-15'),
    (103, 1, 3, 30, '2026-03-20'),
    (105, 3, 2, 150, '2026-03-25')
ON CONFLICT (delivery_id) DO NOTHING;

-- ============================================================
-- Проверочные запросы
-- ============================================================
SELECT 'partner_types' AS table_name, COUNT(*) FROM partner_types
UNION ALL
SELECT 'product_types',               COUNT(*) FROM product_types
UNION ALL
SELECT 'partners',                    COUNT(*) FROM partners
UNION ALL
SELECT 'products',                    COUNT(*) FROM products
UNION ALL
SELECT 'deliveries',                  COUNT(*) FROM deliveries;