# Relationship Descriptions (paste into the Word file)

**Database:** Online Shopping Mall (CUSTOMER, PRODUCT, BUY, DELIVERY)

1. **"Customer" makes "Buys"** (1:M, strong / identifying)
   A customer can make zero to many purchases, while a purchase is made by exactly one customer.
   The minimum cardinality on the BUY side is 0, because a newly registered customer may not have bought anything yet.
   BUY's primary key is (customer_id, buy_no), so customer_id is both a PK and an FK. A purchase cannot exist without its customer, which makes BUY a weak entity.

2. **"Product" is included in "Buys"** (1:M, weak / non-identifying)
   A product can be included in zero to many purchases, while a purchase includes exactly one product.
   The minimum cardinality is 0, because a new product may not have been sold yet.
   PRODUCT.product_id (PK) is referenced by BUY.product_id (FK), which is not part of BUY's primary key.

3. **"Buy" is shipped by "Delivery"** (1:1, weak / non-identifying)
   A purchase has zero or one delivery, while a delivery is for exactly one purchase.
   The minimum cardinality is 0, because a purchase may not be shipped yet. A UNIQUE constraint on DELIVERY(customer_id, buy_no) (FK) enforces the 1:1 relationship.

**Requirement checklist**
| Requirement | Where |
|---|---|
| 3+ tables | 4 tables |
| Weak relationship | Product–Buy, Buy–Delivery |
| Strong relationship | Customer–Buy |
| 1:1 | Buy–Delivery |
| 1:M | Customer–Buy, Product–Buy |
| Minimum cardinality 0 | Customer–Buy, Product–Buy, Buy–Delivery |
| PK / FK | Key icon = PK, red diamond = FK in the diagram |
