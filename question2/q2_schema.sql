CREATE TABLE IF NOT EXISTS "addresses" (
    "id" INTEGER NOT NULL,
    "customer_id" INTEGER NOT NULL,
    "address_type" VARCHAR(29) NOT NULL,
    "postal_code" VARCHAR(29) NOT NULL,
    "street" VARCHAR(55) NOT NULL,
    "number" INTEGER NOT NULL,
    "complement" VARCHAR(28),
    "district" VARCHAR(53) NOT NULL,
    "city" VARCHAR(47) NOT NULL,
    "state" VARCHAR(22) NOT NULL,
    "country" VARCHAR(22) NOT NULL,
    "is_primary" BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS "attributes" (
    "id" INTEGER NOT NULL,
    "name" VARCHAR(30) NOT NULL,
    "data_type" VARCHAR(27) NOT NULL
);

CREATE TABLE IF NOT EXISTS "brands" (
    "id" INTEGER NOT NULL,
    "name" VARCHAR(34) NOT NULL,
    "country" VARCHAR(22),
    "is_active" BOOLEAN NOT NULL,
    "created_at" TIMESTAMP NOT NULL,
    "updated_at" TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS "categories" (
    "id" INTEGER NOT NULL,
    "name" VARCHAR(40) NOT NULL,
    "slug" VARCHAR(40) NOT NULL,
    "parent_category_id" INTEGER,
    "is_active" BOOLEAN NOT NULL,
    "created_at" TIMESTAMP NOT NULL,
    "updated_at" TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS "customers" (
    "id" INTEGER NOT NULL,
    "person_type" VARCHAR(22) NOT NULL,
    "legal_name" VARCHAR(52) NOT NULL,
    "trade_name" VARCHAR(47),
    "tax_id" INTEGER NOT NULL,
    "state_registration" VARCHAR(30),
    "email" VARCHAR(69),
    "phone" VARCHAR(34),
    "is_active" BOOLEAN NOT NULL,
    "created_at" TIMESTAMP NOT NULL,
    "updated_at" TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS "employees" (
    "id" INTEGER NOT NULL,
    "full_name" VARCHAR(45) NOT NULL,
    "cpf" INTEGER NOT NULL,
    "email" VARCHAR(66) NOT NULL,
    "role" VARCHAR(31) NOT NULL,
    "primary_location_id" INTEGER NOT NULL,
    "hire_date" DATE NOT NULL,
    "termination_date" DATE,
    "is_active" BOOLEAN NOT NULL,
    "created_at" TIMESTAMP NOT NULL,
    "updated_at" TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS "fiscal_invoices" (
    "id" INTEGER NOT NULL,
    "order_id" INTEGER NOT NULL,
    "nfe_number" VARCHAR(32) NOT NULL,
    "nfe_access_key" INTEGER NOT NULL,
    "series" INTEGER NOT NULL,
    "issued_at" TIMESTAMP NOT NULL,
    "status" VARCHAR(30) NOT NULL,
    "total_amount" NUMERIC NOT NULL,
    "xml_storage_uri" VARCHAR(89) NOT NULL,
    "created_at" TIMESTAMP NOT NULL,
    "updated_at" TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS "goods_receipt_items" (
    "id" INTEGER NOT NULL,
    "goods_receipt_id" INTEGER NOT NULL,
    "purchase_order_item_id" INTEGER NOT NULL,
    "quantity_received" VARCHAR(26) NOT NULL
);

CREATE TABLE IF NOT EXISTS "goods_receipts" (
    "id" INTEGER NOT NULL,
    "purchase_order_id" INTEGER NOT NULL,
    "received_by_employee_id" INTEGER NOT NULL,
    "received_at" TIMESTAMP NOT NULL,
    "notes" VARCHAR(35),
    "created_at" TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS "locations" (
    "id" INTEGER NOT NULL,
    "name" VARCHAR(36) NOT NULL,
    "location_type" VARCHAR(29) NOT NULL,
    "postal_code" VARCHAR(29) NOT NULL,
    "street" VARCHAR(44) NOT NULL,
    "number" INTEGER NOT NULL,
    "complement" VARCHAR(27),
    "district" VARCHAR(47) NOT NULL,
    "city" VARCHAR(38) NOT NULL,
    "state" VARCHAR(22) NOT NULL,
    "country" VARCHAR(22) NOT NULL,
    "is_active" BOOLEAN NOT NULL,
    "created_at" TIMESTAMP NOT NULL,
    "updated_at" TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS "order_items" (
    "id" INTEGER NOT NULL,
    "order_id" INTEGER NOT NULL,
    "product_variant_id" INTEGER NOT NULL,
    "quantity" INTEGER NOT NULL,
    "unit_price" NUMERIC NOT NULL,
    "icms_rate" NUMERIC NOT NULL,
    "ipi_rate" NUMERIC NOT NULL,
    "line_total" NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS "orders" (
    "id" INTEGER NOT NULL,
    "order_number" VARCHAR(29) NOT NULL,
    "channel" VARCHAR(29) NOT NULL,
    "customer_id" INTEGER NOT NULL,
    "salesperson_id" INTEGER,
    "location_id" INTEGER NOT NULL,
    "status" VARCHAR(29) NOT NULL,
    "subtotal" NUMERIC NOT NULL,
    "discount_amount" NUMERIC NOT NULL,
    "total" NUMERIC NOT NULL,
    "placed_at" TIMESTAMP NOT NULL,
    "created_at" TIMESTAMP NOT NULL,
    "updated_at" TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS "payments" (
    "id" INTEGER NOT NULL,
    "order_id" INTEGER NOT NULL,
    "method" VARCHAR(33) NOT NULL,
    "installments" INTEGER NOT NULL,
    "amount" NUMERIC NOT NULL,
    "status" VARCHAR(28) NOT NULL,
    "paid_at" TIMESTAMP,
    "created_at" TIMESTAMP NOT NULL,
    "updated_at" TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS "product_suppliers" (
    "product_variant_id" INTEGER NOT NULL,
    "supplier_id" INTEGER NOT NULL,
    "supplier_sku" VARCHAR(33),
    "last_quoted_cost" NUMERIC NOT NULL,
    "lead_time_days" INTEGER NOT NULL,
    "is_preferred" BOOLEAN NOT NULL,
    "created_at" TIMESTAMP NOT NULL,
    "updated_at" TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS "product_variants" (
    "id" INTEGER NOT NULL,
    "product_id" INTEGER NOT NULL,
    "sku" VARCHAR(30) NOT NULL,
    "barcode_ean" INTEGER,
    "sale_price" NUMERIC NOT NULL,
    "cost_price" NUMERIC NOT NULL,
    "weight_kg" NUMERIC NOT NULL,
    "icms_rate" NUMERIC NOT NULL,
    "ipi_rate" NUMERIC NOT NULL,
    "is_active" BOOLEAN NOT NULL,
    "created_at" TIMESTAMP NOT NULL,
    "updated_at" TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS "products" (
    "id" INTEGER NOT NULL,
    "name" VARCHAR(43) NOT NULL,
    "description" VARCHAR(68),
    "brand_id" INTEGER NOT NULL,
    "category_id" INTEGER NOT NULL,
    "ncm_code" INTEGER NOT NULL,
    "unit_of_measure" VARCHAR(22) NOT NULL,
    "is_active" BOOLEAN NOT NULL,
    "created_at" TIMESTAMP NOT NULL,
    "updated_at" TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS "purchase_order_items" (
    "id" INTEGER NOT NULL,
    "purchase_order_id" INTEGER NOT NULL,
    "product_variant_id" INTEGER NOT NULL,
    "quantity_ordered" INTEGER NOT NULL,
    "unit_cost" NUMERIC NOT NULL,
    "line_total" NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS "purchase_orders" (
    "id" INTEGER NOT NULL,
    "po_number" VARCHAR(29) NOT NULL,
    "supplier_id" INTEGER NOT NULL,
    "buyer_id" INTEGER NOT NULL,
    "destination_location_id" INTEGER NOT NULL,
    "status" VARCHAR(38) NOT NULL,
    "currency" VARCHAR(23) NOT NULL,
    "subtotal" NUMERIC NOT NULL,
    "total" NUMERIC NOT NULL,
    "placed_at" TIMESTAMP NOT NULL,
    "expected_delivery_at" DATE,
    "created_at" TIMESTAMP NOT NULL,
    "updated_at" TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS "return_items" (
    "id" INTEGER NOT NULL,
    "return_id" INTEGER NOT NULL,
    "order_item_id" INTEGER NOT NULL,
    "quantity" VARCHAR(25) NOT NULL,
    "action" VARCHAR(28) NOT NULL,
    "exchange_variant_id" INTEGER,
    "unit_refund_amount" NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS "returns" (
    "id" INTEGER NOT NULL,
    "return_number" VARCHAR(29) NOT NULL,
    "order_id" INTEGER NOT NULL,
    "customer_id" INTEGER NOT NULL,
    "received_at_location_id" INTEGER NOT NULL,
    "status" VARCHAR(29) NOT NULL,
    "reason" VARCHAR(53),
    "total_refund_amount" NUMERIC NOT NULL,
    "created_at" TIMESTAMP NOT NULL,
    "updated_at" TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS "stock_levels" (
    "product_variant_id" INTEGER NOT NULL,
    "location_id" INTEGER NOT NULL,
    "quantity_on_hand" NUMERIC NOT NULL,
    "reorder_point" TEXT,
    "updated_at" TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS "stock_movements" (
    "id" INTEGER NOT NULL,
    "product_variant_id" INTEGER NOT NULL,
    "location_id" INTEGER NOT NULL,
    "movement_type" VARCHAR(31) NOT NULL,
    "quantity" VARCHAR(27) NOT NULL,
    "reference_table" VARCHAR(34),
    "reference_id" INTEGER,
    "employee_id" INTEGER,
    "notes" VARCHAR(54),
    "occurred_at" TIMESTAMP NOT NULL,
    "created_at" TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS "suppliers" (
    "id" INTEGER NOT NULL,
    "legal_name" VARCHAR(50) NOT NULL,
    "trade_name" VARCHAR(31),
    "country" VARCHAR(22) NOT NULL,
    "tax_id" VARCHAR(34) NOT NULL,
    "tax_id_type" VARCHAR(24) NOT NULL,
    "email" VARCHAR(50) NOT NULL,
    "phone" INTEGER NOT NULL,
    "contact_name" VARCHAR(47) NOT NULL,
    "is_active" BOOLEAN NOT NULL,
    "created_at" TIMESTAMP NOT NULL,
    "updated_at" TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS "variant_attribute_values" (
    "product_variant_id" INTEGER NOT NULL,
    "attribute_id" INTEGER NOT NULL,
    "value" VARCHAR(34) NOT NULL
);
