import pandas as pd


def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        print(f"Загружено {len(df)} записей из {file_path}")
        return df
    except Exception as e:
        raise Exception(f"Ошибка загрузки данных: {e}")
