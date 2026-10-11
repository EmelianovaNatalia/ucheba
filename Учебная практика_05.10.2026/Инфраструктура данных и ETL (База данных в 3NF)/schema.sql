-- ============================================================
-- Задание 1: Проектирование схемы в 3NF
--
-- Таблицы:
--   partner_types  — справочник типов партнёров
--   partners       — информация о партнёрах
--   products       — справочник номенклатуры
--   sales_history  — история реализации
-- ============================================================

-- Удаление таблиц в порядке, обратном зависимостям
DROP TABLE IF EXISTS sales_history  CASCADE;
DROP TABLE IF EXISTS partners       CASCADE;
DROP TABLE IF EXISTS partner_types  CASCADE;
DROP TABLE IF EXISTS products       CASCADE;

-- ── Справочник типов партнёров ────────────────────────────────────────────
CREATE TABLE partner_types (
    partner_type_id SERIAL        PRIMARY KEY,
    type_name       VARCHAR(100)  NOT NULL UNIQUE
);

-- ── Партнёры ──────────────────────────────────────────────────────────────
CREATE TABLE partners (
    partner_id      SERIAL        PRIMARY KEY,
    partner_type_id INTEGER       NOT NULL REFERENCES partner_types(partner_type_id),
    partner_name    VARCHAR(255)  NOT NULL,
    inn             VARCHAR(12)   NOT NULL UNIQUE,
    email           VARCHAR(255)  NOT NULL UNIQUE,
    director        VARCHAR(255),
    phone           VARCHAR(20),
    address         VARCHAR(500),
    rating          INTEGER       DEFAULT 0 CHECK (rating >= 0)
);

-- ── Справочник номенклатуры ───────────────────────────────────────────────
CREATE TABLE products (
    product_id      SERIAL        PRIMARY KEY,
    product_name    VARCHAR(255)  NOT NULL UNIQUE,
    price           DECIMAL(12,2) NOT NULL CHECK (price >= 0)
);

-- ── История реализации ────────────────────────────────────────────────────
CREATE TABLE sales_history (
    sale_id         SERIAL        PRIMARY KEY,
    partner_id      INTEGER       NOT NULL REFERENCES partners(partner_id),
    product_id      INTEGER       NOT NULL REFERENCES products(product_id),
    sale_date       DATE          NOT NULL,
    quantity        INTEGER       NOT NULL CHECK (quantity > 0),
    amount          DECIMAL(14,2) NOT NULL CHECK (amount >= 0)
);
