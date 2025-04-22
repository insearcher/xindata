"""
Скрипт для запуска EDA и сохранения результатов
"""

import os
import json
from src.data_analysis import load_data, analyze_data, print_schema_for_prompt

def main():
    """
    Загружает данные, проводит EDA и сохраняет результаты в JSON файл
    """
    print("Запуск Exploratory Data Analysis (EDA)")
    print("======================================")
    
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
            return
    
    # Загрузка данных
    try:
        df = load_data(data_path)
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        return
    
    # Проведение анализа
    try:
        results = analyze_data(df)
        
        # Вывод схемы данных для промпта
        print("\n" + "="*80 + "\n")
        print_schema_for_prompt(results['schema'])
        
        # Сохранение результатов в JSON файл
        results_path = os.path.join("data", "eda_results.json")
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=4)
        
        print(f"\nРезультаты анализа сохранены в {results_path}")
        
    except Exception as e:
        print(f"Ошибка при проведении анализа: {e}")
        return

if __name__ == "__main__":
    main()
