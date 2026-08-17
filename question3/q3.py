import csv
import os
import argparse
import psycopg


def load_csv(conn, csv_path):
    table_name = os.path.splitext(
        os.path.basename(csv_path)
    )[0]

    with open(csv_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)

        columns = next(reader)

        with conn.cursor() as cur:
            with cur.copy(
                f"""
                COPY "{table_name}" ({', '.join(f'"{col}"' for col in columns)})
                FROM STDIN
                WITH (FORMAT CSV)
                """
            ) as copy:
                for row in reader:
                    copy.write(
                        ",".join(row) + "\n"
                    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "data_dir",
        help="Diretório contendo os arquivos CSV"
    )

    args = parser.parse_args()

    conn = psycopg.connect(
        host="localhost",
        port=5432,
        dbname="csv_schema_test",
        user="postgres",
        password="postgres"
    )

    for filename in os.listdir(args.data_dir):

        if not filename.lower().endswith(".csv"):
            continue

        csv_path = os.path.join(
            args.data_dir,
            filename
        )

        print(f"Carregando {filename}...")

        load_csv(conn, csv_path)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()