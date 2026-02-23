CREATE TABLE chains (
    id SERIAL PRIMARY KEY,
    chain_id VARCHAR(20) UNIQUE NOT NULL, -- מזהה רשת לפי משרד הכלכלה (7296071000113)
    name TEXT NOT NULL
);

CREATE TABLE stores (
    id SERIAL PRIMARY KEY,
    chain_id INTEGER REFERENCES chains(id) ON DELETE CASCADE,
    store_code VARCHAR(10) NOT NULL,
    name TEXT,
    UNIQUE (chain_id, store_code)
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    barcode VARCHAR(50) UNIQUE NOT NULL,
    name TEXT,
    brand TEXT,
    category TEXT,
    image_url TEXT
);

CREATE TABLE prices (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    chain_id INTEGER REFERENCES chains(id) ON DELETE CASCADE,
    store_id INTEGER REFERENCES stores(id) ON DELETE CASCADE,
    price NUMERIC(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'ILS',
    updated_at TIMESTAMP NOT NULL,
    UNIQUE (product_id, chain_id, store_id)
);