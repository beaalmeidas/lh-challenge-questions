import argparse
import os
from dotenv import load_dotenv
from collections import defaultdict, deque
import psycopg2

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def get_tables(cursor):
    cursor.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """
    )

    return {row[0] for row in cursor.fetchall()}


def get_foreign_key_dependencies(cursor):
    cursor.execute(
        """
        SELECT
            tc.table_name AS child_table,
            ccu.table_name AS parent_table
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.constraint_column_usage AS ccu
            ON tc.constraint_name = ccu.constraint_name
            AND tc.table_schema = ccu.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_schema = 'public';
        """
    )

    dependencies = defaultdict(set)

    for child_table, parent_table in cursor.fetchall():
        dependencies[child_table].add(parent_table)

    return dependencies


def get_load_order(cursor, tables):
    dependencies = get_foreign_key_dependencies(cursor)

    for table in tables:
        dependencies.setdefault(table, set())

    indegree = {
        table: len(dependencies[table])
        for table in tables
    }

    children = defaultdict(set)

    for child, parents in dependencies.items():
        for parent in parents:
            children[parent].add(child)

    queue = deque(
        table
        for table, degree in indegree.items()
        if degree == 0
    )

    load_order = []

    while queue:
        table = queue.popleft()
        load_order.append(table)

        for child in children[table]:
            indegree[child] -= 1

            if indegree[child] == 0:
                queue.append(child)

    if len(load_order) != len(tables):
        raise RuntimeError(
            "Não foi possível determinar a ordem de carregamento. "
            "Pode existir um ciclo entre as Foreign Keys."
        )

    return load_order


def quote_identifier(identifier):
    return '"' + identifier.replace('"', '""') + '"'


def load_csv(cursor, csv_path, table_name):
    table_identifier = quote_identifier(table_name)

    copy_sql = f"""
        COPY {table_identifier}
        FROM STDIN
        WITH (
            FORMAT CSV,
            HEADER TRUE,
            DELIMITER ',',
            QUOTE '"',
            ESCAPE '"'
        )
    """

    with open(
        csv_path,
        "r",
        encoding="utf-8",
        newline=""
    ) as csv_file:
        cursor.copy_expert(
            copy_sql,
            csv_file
        )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("csv_dir")

    args = parser.parse_args()

    csv_dir = os.path.abspath(args.csv_dir)

    if not os.path.isdir(csv_dir):
        raise FileNotFoundError(
            f"Diretório não encontrado: {csv_dir}"
        )

    connection = get_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                tables = get_tables(cursor)

                if not tables:
                    raise RuntimeError(
                        "Nenhuma tabela foi encontrada no schema public."
                    )

                load_order = get_load_order(
                    cursor,
                    tables
                )

                print("Ordem de carregamento:")

                for table in load_order:
                    print(f"  - {table}")

                print()

                csv_files = sorted(
                    filename
                    for filename in os.listdir(csv_dir)
                    if filename.lower().endswith(".csv")
                )

                if not csv_files:
                    raise RuntimeError(
                        "Nenhum arquivo CSV encontrado."
                    )

                loaded_tables = set()

                for table_name in load_order:

                    csv_path = os.path.join(
                        csv_dir,
                        f"{table_name}.csv"
                    )

                    if not os.path.isfile(csv_path):
                        print(
                            f"[AVISO] CSV não encontrado para "
                            f"a tabela '{table_name}': "
                            f"{csv_path}"
                        )
                        continue

                    print(
                        f"Carregando {table_name}.csv "
                        f"-> {table_name}"
                    )

                    load_csv(
                        cursor,
                        csv_path,
                        table_name
                    )

                    loaded_tables.add(table_name)

                    print(
                        f"[OK] {table_name}"
                    )

                csv_tables = {
                    os.path.splitext(filename)[0]
                    for filename in csv_files
                }

                unknown_csvs = csv_tables - tables

                if unknown_csvs:
                    raise RuntimeError(
                        "Existem CSVs sem tabela correspondente "
                        f"no banco: {sorted(unknown_csvs)}"
                    )

                print()
                print(
                    f"Carregamento concluído: "
                    f"{len(loaded_tables)} tabelas."
                )

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()