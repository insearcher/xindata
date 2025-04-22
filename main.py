"""
Главный модуль приложения для анализа данных о фрилансерах
"""

import os
import pandas as pd
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

def main():
    """
    Основная функция приложения
    """
    print("Система анализа данных о фрилансерах")
    print("====================================")
    
    # Путь к файлу с данными
    data_path = os.path.join("data", "freelancer_earnings_bd.csv")
    
    # Проверка существования файла
    if not os.path.exists(data_path):
        # Если полный файл отсутствует, используем тестовый
        test_data_path = os.path.join("data", "freelancer_earnings_bd_100.csv")
        if os.path.exists(test_data_path):
            print(f"Файл {data_path} не найден, используем тестовый файл {test_data_path}")
            data_path = test_data_path
        else:
            print(f"Ошибка: Файл с данными не найден по пути {data_path}")
            print("Пожалуйста, скачайте датасет по ссылке: https://www.kaggle.com/datasets/shohinurpervezshohan/freelancer-earnings-and-job-trends")
            print("и поместите его в папку data/")
            return
    
    # Загрузка данных
    try:
        df = pd.read_csv(data_path)
        print(f"Загружено {len(df)} записей из файла {data_path}")
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        return
    
    # TODO: Реализовать основной функционал приложения
    # На данный момент это просто заготовка для дальнейшей разработки
    
    print("Система готова. Продолжим разработку в рамках Фазы 1.")

if __name__ == "__main__":
    main()
