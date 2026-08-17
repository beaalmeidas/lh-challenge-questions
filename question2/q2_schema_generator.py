import csv
import os
import re
import argparse
from datetime import datetime


# CONFIGURACOES E UTILS DE INFERENCIA ---------------------------------------
DATETIME_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
]

DATE_FORMATS = [
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%d-%m-%Y",
]

BOOLEAN_VALUES = {
    "true", "false", "t", "f", "1", "0", "yes", "no", "sim", "nao", "não"
}

INT_RE = re.compile(r"^[+-]?\d+$")
FLOAT_RE = re.compile(r"^[+-]?\d+([.,]\d+)?$")

INTEGER_MIN = -2_147_483_648
INTEGER_MAX = 2_147_483_647

BIGINT_MIN = -9_223_372_036_854_775_808
BIGINT_MAX = 9_223_372_036_854_775_807


def is_empty(value: str) -> bool:
    return value is None or value.strip() == ""


def is_integer(value: str) -> bool:
    return bool(INT_RE.match(value.strip()))


def is_float(value: str) -> bool:
    v = value.strip()
    if not FLOAT_RE.match(v):
        return False
    return ("." in v) or ("," in v)


def is_boolean(value: str) -> bool:
    return value.strip().lower() in BOOLEAN_VALUES


def is_date(value: str) -> bool:
    v = value.strip()
    for fmt in DATE_FORMATS:
        try:
            datetime.strptime(v, fmt)
            return True
        except ValueError:
            continue
    return False


def is_datetime(value: str) -> bool:
    v = value.strip()
    for fmt in DATETIME_FORMATS:
        try:
            datetime.strptime(v, fmt)
            return True
        except ValueError:
            continue
    return False

def classify_integer(value: str) -> str:
    v = value.strip()

    if not INT_RE.match(v):
        return None

    number = int(v)

    if INTEGER_MIN <= number <= INTEGER_MAX:
        return "INTEGER"

    if BIGINT_MIN <= number <= BIGINT_MAX:
        return "BIGINT"

    return "NUMERIC"


TYPE_CHECKS = [
    ("BOOLEAN", is_boolean),
    ("TIMESTAMP", is_datetime),
    ("DATE", is_date),
]

TYPE_RANK = ["BOOLEAN", "INTEGER", "NUMERIC", "DATE", "TIMESTAMP", "TEXT"]


# verifica e categoriza cada valor nas tabelas
def classify_value(value: str) -> str:
    if is_empty(value):
        return None

    for type_name, check_fn in TYPE_CHECKS:
        if check_fn(value):
            return type_name

    if is_integer(value):
        return classify_integer(value)

    if is_float(value):
        return "NUMERIC"

    return "TEXT"


# descobre o tipo final da coluna apos analisar todos os valores
def merge_types(current: str, new: str) -> str:
    if current is None:
        return new
    if current == new:
        return current

    promotions = {
        frozenset({"INTEGER", "NUMERIC"}): "NUMERIC",
        frozenset({"DATE", "TIMESTAMP"}): "TIMESTAMP",
        frozenset({"BOOLEAN", "INTEGER"}): "INTEGER",
    }
    key = frozenset({current, new})
    if key in promotions:
        return promotions[key]

    return "TEXT"



# RELACIONAMENTOS ENTRE TABELAS ---------------------------------------------

PRIMARY_KEYS = {
    "addresses": ["id"],
    "attributes": ["id"],
    "brands": ["id"],
    "categories": ["id"],
    "customers": ["id"],
    "employees": ["id"],
    "fiscal_invoices": ["id"],
    "goods_receipt_items": ["id"],
    "goods_receipts": ["id"],
    "locations": ["id"],
    "order_items": ["id"],
    "orders": ["id"],
    "payments": ["id"],
    "product_variants": ["id"],
    "products": ["id"],
    "purchase_order_items": ["id"],
    "purchase_orders": ["id"],
    "return_items": ["id"],
    "returns": ["id"],
    "stock_movements": ["id"],
    "suppliers": ["id"],

    "product_suppliers": [
        "product_variant_id",
        "supplier_id"
    ],

    "stock_levels": [
        "product_variant_id",
        "location_id"
    ],

    "variant_attribute_values": [
        "product_variant_id",
        "attribute_id"
    ],
}


FOREIGN_KEYS = {
    "addresses": [
        ("customer_id", "customers", "id"),
    ],

    "employees": [
        ("primary_location_id", "locations", "id"),
    ],

    "fiscal_invoices": [
        ("order_id", "orders", "id"),
    ],

    "goods_receipt_items": [
        ("goods_receipt_id", "goods_receipts", "id"),
        ("purchase_order_item_id", "purchase_order_items", "id"),
    ],

    "goods_receipts": [
        ("purchase_order_id", "purchase_orders", "id"),
        ("received_by_employee_id", "employees", "id"),
    ],

    "order_items": [
        ("order_id", "orders", "id"),
        ("product_variant_id", "product_variants", "id"),
    ],

    "orders": [
        ("customer_id", "customers", "id"),
        ("salesperson_id", "employees", "id"),
        ("location_id", "locations", "id"),
    ],

    "payments": [
        ("order_id", "orders", "id"),
    ],

    "product_suppliers": [
        ("product_variant_id", "product_variants", "id"),
        ("supplier_id", "suppliers", "id"),
    ],

    "product_variants": [
        ("product_id", "products", "id"),
    ],

    "products": [
        ("brand_id", "brands", "id"),
        ("category_id", "categories", "id"),
    ],

    "purchase_order_items": [
        ("purchase_order_id", "purchase_orders", "id"),
        ("product_variant_id", "product_variants", "id"),
    ],

    "purchase_orders": [
        ("supplier_id", "suppliers", "id"),
        ("buyer_id", "employees", "id"),
        ("destination_location_id", "locations", "id"),
    ],

    "return_items": [
        ("return_id", "returns", "id"),
        ("order_item_id", "order_items", "id"),
        ("exchange_variant_id", "product_variants", "id"),
    ],

    "returns": [
        ("order_id", "orders", "id"),
        ("customer_id", "customers", "id"),
        ("received_at_location_id", "locations", "id"),
    ],

    "stock_levels": [
        ("product_variant_id", "product_variants", "id"),
        ("location_id", "locations", "id"),
    ],

    "stock_movements": [
        ("product_variant_id", "product_variants", "id"),
        ("location_id", "locations", "id"),
        ("employee_id", "employees", "id"),
    ],

    "variant_attribute_values": [
        ("product_variant_id", "product_variants", "id"),
        ("attribute_id", "attributes", "id"),
    ],
}


# UTILS DE TABELA E COLUNA --------------------------------------------------

# garante nome de arquivo valido
def sanitize_identifier(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9_]+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    if not name:
        name = "coluna"
    if name[0].isdigit():
        name = f"col_{name}"
    return name


def guarantee_different_column_names(columns):
    seen = {}
    result = []
    for col in columns:
        if col not in seen:
            seen[col] = 0
            result.append(col)
        else:
            seen[col] += 1
            result.append(f"{col}_{seen[col]}")
    return result



# UTILS DE TABELA E COLUNA --------------------------------------------------

# verifica tipo de separador do arquivo
def infer_separator(sample_text: str) -> csv.Dialect:
    try:
        return csv.Sniffer().sniff(sample_text, delimiters=";,|\t")
    except csv.Error:
        return csv.get_dialect("excel")


# orquestradora para as utils
def analyze_csv(filepath: str, sample_size: int = 0):
    with open(filepath, "r", encoding="utf-8-sig", newline="") as f:
        sample = f.read(8192)
        f.seek(0)

        separator = infer_separator(sample) if sample.strip() else csv.get_dialect("excel")
        reader = csv.reader(f, separator)

        try:
            raw_header = next(reader)
        except StopIteration:
            return [], {}, {}, {}

        raw_header = [h if h is not None else f"col_{i}" for i, h in enumerate(raw_header)]
        columns = guarantee_different_column_names([sanitize_identifier(h) for h in raw_header])

        col_types = {c: None for c in columns}
        col_nullable = {c: False for c in columns}
        col_maxlen = {c: 0 for c in columns}

        row_count = 0
        for row in reader:
            if sample_size and row_count >= sample_size:
                break
            row = row + [""] * (len(columns) - len(row))
            for col, value in zip(columns, row):
                if is_empty(value):
                    col_nullable[col] = True
                    continue
                col_maxlen[col] = max(col_maxlen[col], len(value))
                value_type = classify_value(value)
                col_types[col] = merge_types(col_types[col], value_type)
            row_count += 1

        for col in columns:
            if col_types[col] is None:
                col_types[col] = "TEXT"
                col_nullable[col] = True

        return columns, col_types, col_nullable, col_maxlen


# gera os comandos que ditam os relacionamentos entre tabelas
def generate_foreign_keys() -> str:
    statements = []

    for table_name, foreign_keys in FOREIGN_KEYS.items():
        for column, ref_table, ref_column in foreign_keys:

            constraint_name = (
                f"fk_{table_name}_{column}"
            )

            statement = (
                f'ALTER TABLE "{table_name}" '
                f'ADD CONSTRAINT "{constraint_name}" '
                f'FOREIGN KEY ("{column}") '
                f'REFERENCES "{ref_table}" ("{ref_column}");'
            )

            statements.append(statement)

    return "\n\n".join(statements)


# SQL AND SCHEMA FILE GENERATION --------------------------------------------

# infere o tipo final para valores de texto
def sql_type_for(col_type: str, max_len: int) -> str:
    if col_type == "TEXT":
        if max_len and max_len <= 255:
            return f"VARCHAR({max(max_len, 1) + 20})"
        return "TEXT"
    return col_type


def generate_create_table(table_name: str, columns, col_types, col_nullable, col_maxlen) -> str:
    lines = [f'CREATE TABLE IF NOT EXISTS "{table_name}" (']
    col_defs = []
    for col in columns:
        sql_type = sql_type_for(col_types[col], col_maxlen[col])
        null_clause = "" if col_nullable[col] else " NOT NULL"
        col_defs.append(f'    "{col}" {sql_type}{null_clause}')

    primary_key = PRIMARY_KEYS.get(table_name)

    if primary_key:
        pk_columns = ", ".join(
            f'"{col}"'
            for col in primary_key
        )

        col_defs.append(
            f"    PRIMARY KEY ({pk_columns})"
        )

    lines.append(",\n".join(col_defs))
    lines.append(");")
    return "\n".join(lines)


def generate_schema(input_dir: str, output_file: str, sample_size: int = 0):
    csv_files = sorted(
        f for f in os.listdir(input_dir) if f.lower().endswith(".csv")
    )

    if not csv_files:
        print(f"\n--- Nenhum arquivo .csv encontrado em: {input_dir}")
        return

    print("\n")
    statements = []
    for csv_file in csv_files:
        filepath = os.path.join(input_dir, csv_file)
        table_name = sanitize_identifier(os.path.splitext(csv_file)[0])

        print(f"--- Processando: {csv_file}")
        columns, col_types, col_nullable, col_maxlen = analyze_csv(filepath, sample_size)

        if not columns:
            print(f"  [aviso] arquivo vazio, ignorado: {csv_file}")
            continue

        ddl = generate_create_table(table_name, columns, col_types, col_nullable, col_maxlen)
        statements.append(ddl)

    schema_sql = "\n\n".join(statements)
    foreign_keys_sql = generate_foreign_keys()

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(schema_sql)
        f.write("\n\n")

        f.write("-- FOREIGN KEYS --------------------------------------------------\n\n")
        f.write(foreign_keys_sql)
        f.write("\n")

    print(f"\n--- Arquivo gerado com sucesso: {os.path.abspath(output_file)}")
    print("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir")
    parser.add_argument("--out", default="q2_schema.sql")
    parser.add_argument("--sample", type=int, default=0)

    args = parser.parse_args()

    generate_schema(
        args.input_dir,
        args.out,
        args.sample
    )


if __name__ == "__main__":
    main()