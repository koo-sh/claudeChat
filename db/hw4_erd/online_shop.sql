-- HW4 ERD: Online Shopping Mall (customer / product / buy + delivery)
-- Import into MySQL Workbench:
--   File > Import > Reverse Engineer MySQL Create Script... > select this file
--   > check "Place imported objects on a diagram" > Execute

CREATE SCHEMA IF NOT EXISTS online_shop;
USE online_shop;

CREATE TABLE customer (
  customer_id INT          NOT NULL AUTO_INCREMENT,
  name        VARCHAR(50)  NOT NULL,
  email       VARCHAR(100) NOT NULL,
  PRIMARY KEY (customer_id)
);

CREATE TABLE product (
  product_id INT           NOT NULL AUTO_INCREMENT,
  name       VARCHAR(100)  NOT NULL,
  price      DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (product_id)
);

-- customer -> buy : 1:M, strong (identifying). customer_id is part of the PK.
-- product  -> buy : 1:M, weak (non-identifying). product_id is only an FK.
CREATE TABLE buy (
  customer_id INT NOT NULL,
  buy_no      INT NOT NULL,
  product_id  INT NOT NULL,
  PRIMARY KEY (customer_id, buy_no),
  CONSTRAINT fk_buy_customer
    FOREIGN KEY (customer_id) REFERENCES customer (customer_id),
  CONSTRAINT fk_buy_product
    FOREIGN KEY (product_id) REFERENCES product (product_id)
);

-- buy -> delivery : 1:1, weak (non-identifying).
-- The UNIQUE foreign key allows at most one delivery per purchase.
CREATE TABLE delivery (
  delivery_id INT NOT NULL AUTO_INCREMENT,
  customer_id INT NOT NULL,
  buy_no      INT NOT NULL,
  PRIMARY KEY (delivery_id),
  UNIQUE KEY uq_delivery_buy (customer_id, buy_no),
  CONSTRAINT fk_delivery_buy
    FOREIGN KEY (customer_id, buy_no) REFERENCES buy (customer_id, buy_no)
);
