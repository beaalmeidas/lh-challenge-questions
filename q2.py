import pandas as pd

#botar para processar todos os csvs num diretorio
#funcao para ajeitar os nomes de tabela e de coluna?


def process_file(self, file_path):
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        df = df.loc[:, (df != '*').any(axis=0)]
        df.columns = df.columns.str.replace('[^a-zA-Z]', '_', regex=True)
        df.columns = [a + str(i) for i, a in enumerate(df.columns)]
        df.to_sql(self.table_name, self.engine, if_exists='append', index=False, schema='dbo', chunksize=1000)
    except Exception as e:
        self.handle_error(file_path, e)