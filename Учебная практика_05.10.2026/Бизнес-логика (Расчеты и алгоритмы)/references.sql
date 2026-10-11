CREATE TABLE IF NOT EXISTS product_types (
    product_type_id   SERIAL        PRIMARY KEY,
    type_name         VARCHAR(100)  NOT NULL UNIQUE,
    type_coefficient  DECIMAL(6,3)  NOT NULL CHECK (type_coefficient > 0)
);

CREATE TABLE IF NOT EXISTS materials (
    material_id    SERIAL        PRIMARY KEY,
    material_name  VARCHAR(100)  NOT NULL UNIQUE,
    unit           VARCHAR(20)   NOT NULL
);

INSERT INTO product_types (type_name, type_coefficient) VALUES
    ('Стандарт', 1.000),
    ('Премиум',  1.500),
    ('Эконом',   0.750)
ON CONFLICT (type_name) DO NOTHING;

INSERT INTO materials (material_name, unit) VALUES
    ('Ламинат',  'кв.м'),
    ('Паркет',   'кв.м'),
    ('Плитка',   'кв.м')
ON CONFLICT (material_name) DO NOTHING;