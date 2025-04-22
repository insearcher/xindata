"""
Модуль для первичного анализа данных о фрилансерах
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(file_path):
    """
    Загружает данные из CSV файла.
    
    Args:
        file_path (str): Путь к CSV файлу
        
    Returns:
        pd.DataFrame: Загруженный датафрейм
    """
    df = pd.read_csv(file_path)
    print(f"Dataset shape: {df.shape}")
    return df

def analyze_data(df):
    """
    Проводит первичный анализ данных.
    
    Args:
        df (pd.DataFrame): Датафрейм для анализа
        
    Returns:
        dict: Словарь с результатами анализа
    """
    results = {}
    
    # Базовые статистики
    print("Basic information:")
    print(df.info())
    
    print("\nBasic statistics:")
    print(df.describe())
    
    # Проверка пропущенных значений
    missing_values = df.isnull().sum()
    print("\nMissing values:")
    print(missing_values)
    
    # Анализ категориальных переменных
    categorical_columns = ['Job_Category', 'Platform', 'Experience_Level', 
                          'Client_Region', 'Payment_Method', 'Project_Type']
    
    for col in categorical_columns:
        print(f"\n{col} value counts:")
        print(df[col].value_counts())
    
    # Сохраняем результаты для использования в промпте LLM
    results['schema'] = get_schema(df)
    
    # Анализ примеров вопросов из задания
    results['example_questions'] = analyze_example_questions(df)
    
    return results

def get_schema(df):
    """
    Получает схему данных для использования в промпте LLM.
    
    Args:
        df (pd.DataFrame): Датафрейм для анализа
        
    Returns:
        list: Список словарей с информацией о колонках
    """
    schema = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        unique_values = None
        
        if df[col].dtype == 'object':
            unique_values = df[col].unique().tolist()
            if len(unique_values) > 10:  # Если слишком много уникальных значений
                unique_values = f"{len(unique_values)} уникальных значений"
        
        schema.append({
            'name': col,
            'type': dtype,
            'unique_values': unique_values
        })
    
    return schema

def analyze_example_questions(df):
    """
    Анализирует примеры вопросов из задания.
    
    Args:
        df (pd.DataFrame): Датафрейм для анализа
        
    Returns:
        dict: Словарь с результатами анализа
    """
    results = {}
    
    # 1. Насколько выше доход у фрилансеров, принимающих оплату в криптовалюте, по сравнению с другими способами оплаты?
    crypto_earnings = df[df['Payment_Method'] == 'Cryptocurrency']['Earnings_USD'].mean()
    other_earnings = df[df['Payment_Method'] != 'Cryptocurrency']['Earnings_USD'].mean()
    difference = crypto_earnings - other_earnings
    percentage = (difference / other_earnings) * 100
    
    results['crypto_vs_other'] = {
        'crypto_earnings': crypto_earnings,
        'other_earnings': other_earnings,
        'difference': difference,
        'percentage': percentage
    }
    
    # 2. Как распределяется доход фрилансеров в зависимости от региона проживания?
    region_earnings = df.groupby('Client_Region')['Earnings_USD'].agg(['mean', 'median', 'std', 'count']).reset_index()
    region_earnings = region_earnings.sort_values(by='mean', ascending=False)
    
    results['region_earnings'] = region_earnings.to_dict('records')
    
    # 3. Какой процент фрилансеров, считающих себя экспертами, выполнил менее 100 проектов?
    experts = df[df['Experience_Level'] == 'Expert']
    experts_less_than_100 = experts[experts['Job_Completed'] < 100]
    percentage = (len(experts_less_than_100) / len(experts)) * 100
    
    results['experts_less_than_100'] = {
        'total_experts': len(experts),
        'experts_less_than_100': len(experts_less_than_100),
        'percentage': percentage
    }
    
    return results

def print_schema_for_prompt(schema):
    """
    Выводит схему данных в формате для использования в промпте LLM.
    
    Args:
        schema (list): Список словарей с информацией о колонках
    """
    print("Схема данных для промпта LLM:")
    for item in schema:
        print(f"{item['name']} ({item['type']})")
        if item['unique_values'] is not None and isinstance(item['unique_values'], list):
            print(f"  Уникальные значения: {', '.join(map(str, item['unique_values']))}")
        elif item['unique_values'] is not None:
            print(f"  {item['unique_values']}")
        print()

if __name__ == "__main__":
    data_path = "../data/freelancer_earnings_bd.csv"
    df = load_data(data_path)
    results = analyze_data(df)
    
    print("\n" + "="*80 + "\n")
    print_schema_for_prompt(results['schema'])
    
    print("\n" + "="*80 + "\n")
    print("Результаты анализа примеров вопросов:")
    
    crypto = results['example_questions']['crypto_vs_other']
    print("\n1. Насколько выше доход у фрилансеров, принимающих оплату в криптовалюте, по сравнению с другими способами оплаты?")
    print(f"Средний доход фрилансеров, принимающих оплату в криптовалюте: ${crypto['crypto_earnings']:.2f}")
    print(f"Средний доход фрилансеров, использующих другие способы оплаты: ${crypto['other_earnings']:.2f}")
    print(f"Разница: ${crypto['difference']:.2f} ({crypto['percentage']:.2f}%)")
    
    print("\n2. Как распределяется доход фрилансеров в зависимости от региона проживания?")
    for region in results['example_questions']['region_earnings']:
        print(f"{region['Client_Region']}: ${region['mean']:.2f} (медиана: ${region['median']:.2f}, кол-во: {region['count']})")
    
    experts = results['example_questions']['experts_less_than_100']
    print("\n3. Какой процент фрилансеров, считающих себя экспертами, выполнил менее 100 проектов?")
    print(f"Всего экспертов: {experts['total_experts']}")
    print(f"Экспертов с менее чем 100 проектами: {experts['experts_less_than_100']}")
    print(f"Процент: {experts['percentage']:.2f}%")
