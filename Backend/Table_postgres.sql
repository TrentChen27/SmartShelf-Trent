-- Region table:
CREATE TABLE IF NOT EXISTS Region (
    id              SERIAL PRIMARY KEY,
    region_name     VARCHAR(70) NOT NULL,
    region_manager  INT
);

-- Product table: 
CREATE TABLE IF NOT EXISTS Product (
    id                SERIAL PRIMARY KEY,
    product_name      VARCHAR(140) NOT NULL,
    price             BIGINT NOT NULL,
    kind              VARCHAR(70),
    description       TEXT,
    image_url         VARCHAR(255)
);

-- OnlineAccount table: 
CREATE TABLE IF NOT EXISTS OnlineAccount (
    online_id SERIAL PRIMARY KEY,
    passwd    VARCHAR(140) NOT NULL,
    email     VARCHAR(70) UNIQUE NOT NULL,
    name      VARCHAR(70)
);

-- Employee table: 
CREATE TABLE IF NOT EXISTS Employee (
    id         SERIAL PRIMARY KEY,
    online_id  INT,
    job_title  VARCHAR(70),
    salary     BIGINT,
    FOREIGN KEY (online_id) REFERENCES OnlineAccount(online_id)
);

-- Address table: 
CREATE TABLE IF NOT EXISTS Address (
    id         SERIAL PRIMARY KEY,
    state      VARCHAR(20),
    city       VARCHAR(40),
    zipcode    INT,
    address_1  VARCHAR(70),
    address_2  VARCHAR(70)
);

-- Customer table: 
CREATE TABLE IF NOT EXISTS Customer (
    id          SERIAL PRIMARY KEY,
    online_id   INT,
    kind        INT,  -- 0=home, 1=biz
    address_id  INT,
    FOREIGN KEY (online_id) REFERENCES OnlineAccount(online_id),
    FOREIGN KEY (address_id) REFERENCES Address(id)
);

-- Store table: 
CREATE TABLE IF NOT EXISTS Store (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(70) NOT NULL,
    address_id  INT,
    manager_id  INT,
    region_id   INT,
    FOREIGN KEY (address_id) REFERENCES Address(id),
    FOREIGN KEY (manager_id) REFERENCES Employee(id),
    FOREIGN KEY (region_id) REFERENCES Region(id)
);

-- SalesPerson table: 
CREATE TABLE IF NOT EXISTS SalesPerson (
    id           SERIAL PRIMARY KEY,
    store_id     INT NOT NULL,
    employee_id  INT NOT NULL UNIQUE,
    FOREIGN KEY (store_id) REFERENCES Store(id),
    FOREIGN KEY (employee_id) REFERENCES Employee(id)
);

-- Home customer table
CREATE TABLE IF NOT EXISTS Home (
    id              INT PRIMARY KEY,
    marriage_status INT,  -- 0=single, 1=married, 2=divorced, 3=widowed
    gender          VARCHAR(20),
    age             INT,
    income          BIGINT,
    sales_id        INT,
    FOREIGN KEY (id) REFERENCES Customer(id),
    FOREIGN KEY (sales_id) REFERENCES SalesPerson(employee_id)
);

-- Business customer table
CREATE TABLE IF NOT EXISTS Business (
    id            INT PRIMARY KEY,
    company_name  VARCHAR(140),
    category      VARCHAR(70),
    gross_income  BIGINT,
    sales_id      INT,
    FOREIGN KEY (id) REFERENCES Customer(id),
    FOREIGN KEY (sales_id) REFERENCES SalesPerson(employee_id)
);

-- StoreInventory table 
CREATE TABLE IF NOT EXISTS StoreInventory (
    id          SERIAL PRIMARY KEY,
    store_id    INT NOT NULL,
    product_id  INT NOT NULL,
    stock       INT NOT NULL,
    FOREIGN KEY (store_id) REFERENCES Store(id),
    FOREIGN KEY (product_id) REFERENCES Product(id),
    UNIQUE (store_id, product_id)
);

-- Orders table: 
CREATE TABLE IF NOT EXISTS Orders (
    id              SERIAL PRIMARY KEY,
    customer_id     INT NOT NULL,
    store_id        INT NOT NULL,
    sales_id        INT NOT NULL,
    order_date      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    pickup_date     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount    BIGINT,
    payment_status  BOOLEAN DEFAULT FALSE,   -- false=unpaid, true=paid
    pickup_status   INT DEFAULT 0,           -- 0=waiting for pickup, 1=picked up, 2=cancel
    FOREIGN KEY (customer_id) REFERENCES Customer(id),
    FOREIGN KEY (store_id) REFERENCES Store(id),
    FOREIGN KEY (sales_id) REFERENCES SalesPerson(employee_id)
);

-- OrderItem table: 
CREATE TABLE IF NOT EXISTS OrderItem (
    id          SERIAL PRIMARY KEY,
    order_id    INT NOT NULL,
    product_id  INT NOT NULL,
    quantity    INT NOT NULL,
    sub_price   BIGINT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(id),
    FOREIGN KEY (product_id) REFERENCES Product(id)
);
