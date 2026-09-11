-- ============================================================
-- schema.sql
-- Схема базы данных для системы управления партнёрами (3NF)
-- ============================================================

-- Удаление таблиц в порядке зависимостей (сначала дочерние)
DROP TABLE IF EXISTS deliveries    CASCADE;
DROP TABLE IF EXISTS products      CASCADE;
DROP TABLE IF EXISTS partners      CASCADE;
DROP TABLE IF EXISTS product_types CASCADE;
DROP TABLE IF EXISTS partner_types CASCADE;

-- Справочник типов партнёров
CREATE TABLE partner_types (
    partner_type_id SERIAL PRIMARY KEY,
    type_name       VARCHAR(100) NOT NULL UNIQUE
);

-- Партнёры
CREATE TABLE partners (
    partner_id      SERIAL PRIMARY KEY,
    partner_type_id INT          NOT NULL,
    company_name    VARCHAR(200) NOT NULL,
    inn             VARCHAR(12)  NOT NULL UNIQUE,
    director        VARCHAR(150) NOT NULL,
    email           VARCHAR(150) NOT NULL UNIQUE,
    phone           VARCHAR(20)  NOT NULL,
    address         VARCHAR(255) NOT NULL,
    rating          INT          NOT NULL DEFAULT 0,

    CONSTRAINT fk_partners_type
        FOREIGN KEY (partner_type_id)
        REFERENCES partner_types(partner_type_id)
        ON DELETE RESTRICT
);

-- Справочник типов продукции
CREATE TABLE product_types (
    product_type_id SERIAL PRIMARY KEY,
    type_name       VARCHAR(100) NOT NULL UNIQUE
);

-- Продукция
CREATE TABLE products (
    product_id      SERIAL PRIMARY KEY,
    product_type_id INT             NOT NULL,
    product_name    VARCHAR(200)    NOT NULL,
    article         VARCHAR(50)     NOT NULL UNIQUE,
    unit            VARCHAR(20)     NOT NULL DEFAULT 'шт.',
    min_price       DECIMAL(10, 2)  NOT NULL,

    CONSTRAINT fk_products_type
        FOREIGN KEY (product_type_id)
        REFERENCES product_types(product_type_id)
        ON DELETE RESTRICT
);

-- История отгрузок
CREATE TABLE deliveries (
    delivery_id   SERIAL PRIMARY KEY,
    partner_id    INT  NOT NULL,
    product_id    INT  NOT NULL,
    quantity      INT  NOT NULL CHECK (quantity > 0),
    delivery_date DATE NOT NULL,

    CONSTRAINT fk_deliveries_partner
        FOREIGN KEY (partner_id)
        REFERENCES partners(partner_id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_deliveries_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE RESTRICT
);
