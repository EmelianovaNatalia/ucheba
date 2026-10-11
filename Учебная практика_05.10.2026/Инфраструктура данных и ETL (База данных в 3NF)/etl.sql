-- ============================================================
-- Задание 1: ETL — импорт и очистка данных
--
-- Источники:
--   partners_raw.csv     — сырые данные партнёров
--   products_raw.csv     — сырые данные номенклатуры
--   sales_history_raw.csv — история реализации (разные форматы дат,
--                           лишние пробелы, битый FK partner_id=999)
-- ============================================================

-- ── Шаг 1: Загрузка сырых данных во временные таблицы ────────────────────

CREATE TEMP TABLE partners_raw (
    partner_id   INTEGER,
    partner_name TEXT,
    inn          TEXT,
    email        TEXT
);

CREATE TEMP TABLE products_raw (
    product_id   INTEGER,
    product_name TEXT,
    price        TEXT
);

CREATE TEMP TABLE sales_history_raw (
    sale_id    INTEGER,
    partner_id INTEGER,
    product_id INTEGER,
    sale_date  TEXT,
    quantity   INTEGER,
    amount     TEXT
);

-- Импорт CSV-файлов (пути указаны относительно расположения файлов проекта)
\COPY partners_raw      FROM 'partners_raw.csv'      WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\COPY products_raw      FROM 'products_raw.csv'      WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\COPY sales_history_raw FROM 'sales_history_raw.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

-- ── Шаг 2: Наполнение справочника типов партнёров ────────────────────────

-- Типы определяются по префиксу наименования партнёра
INSERT INTO partner_types (type_name) VALUES
    ('ООО'),
    ('ИП'),
    ('АО')
ON CONFLICT (type_name) DO NOTHING;

-- ── Шаг 3: Очистка и импорт партнёров ────────────────────────────────────

-- TRIM убирает лишние пробелы в имени и email
-- Тип партнёра определяется по первому слову наименования
INSERT INTO partners (partner_id, partner_type_id, partner_name, inn, email)
SELECT
    r.partner_id,
    pt.partner_type_id,
    TRIM(r.partner_name),
    TRIM(r.inn),
    TRIM(r.email)
FROM partners_raw r
JOIN partner_types pt
    ON pt.type_name = SPLIT_PART(TRIM(r.partner_name), ' ', 1);

-- Сброс счётчика последовательности после явной вставки с ID
SELECT SETVAL('partners_partner_id_seq', (SELECT MAX(partner_id) FROM partners));

-- ── Шаг 4: Очистка и импорт номенклатуры ─────────────────────────────────

-- TRIM убирает лишние пробелы в названии товара
INSERT INTO products (product_id, product_name, price)
SELECT
    product_id,
    TRIM(product_name),
    REPLACE(price, ',', '.')::DECIMAL(12,2)
FROM products_raw;

SELECT SETVAL('products_product_id_seq', (SELECT MAX(product_id) FROM products));

-- ── Шаг 5: Нормализация дат и импорт истории продаж ──────────────────────

-- Аномалии дат в исходном файле:
--   25.10.2023   — формат ДД.ММ.ГГГГ
--   2023/10/26   — формат ГГГГ/ММ/ДД
--   2023-10-27   — корректный формат ISO
--   28-10-2023   — формат ДД-ММ-ГГГГ
--   2023.10.29   — формат ГГГГ.ММ.ДД
--   2023-10-30   — корректный формат ISO (с пробелами — TRIM)
--   Строка с partner_id=999 исключается: партнёр не существует (битый FK)

INSERT INTO sales_history (sale_id, partner_id, product_id, sale_date, quantity, amount)
SELECT
    r.sale_id,
    r.partner_id,
    r.product_id,
    CASE
        WHEN TRIM(r.sale_date) ~ '^\d{2}\.\d{2}\.\d{4}$'
            THEN TO_DATE(TRIM(r.sale_date), 'DD.MM.YYYY')
        WHEN TRIM(r.sale_date) ~ '^\d{4}/\d{2}/\d{2}$'
            THEN TO_DATE(TRIM(r.sale_date), 'YYYY/MM/DD')
        WHEN TRIM(r.sale_date) ~ '^\d{4}-\d{2}-\d{2}$'
            THEN TO_DATE(TRIM(r.sale_date), 'YYYY-MM-DD')
        WHEN TRIM(r.sale_date) ~ '^\d{2}-\d{2}-\d{4}$'
            THEN TO_DATE(TRIM(r.sale_date), 'DD-MM-YYYY')
        WHEN TRIM(r.sale_date) ~ '^\d{4}\.\d{2}\.\d{2}$'
            THEN TO_DATE(TRIM(r.sale_date), 'YYYY.MM.DD')
    END,
    r.quantity,
    REPLACE(r.amount::TEXT, ',', '.')::DECIMAL(14,2)
FROM sales_history_raw r
WHERE r.partner_id IN (SELECT partner_id FROM partners);

SELECT SETVAL('sales_history_sale_id_seq', (SELECT MAX(sale_id) FROM sales_history));

-- ── Шаг 6: Удаление временных таблиц ─────────────────────────────────────

DROP TABLE partners_raw;
DROP TABLE products_raw;
DROP TABLE sales_history_raw;