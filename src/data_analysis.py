"""
Модуль для первичного анализа данных о фрилансерах
"""

import pandas as pd
import numpy as np
import json
import os

def load_data(file_path):
    """
    Загружает данные из CSV файла.
    
    Args:
        file_path (str): Путь к CSV файлу
        
    Returns:
        pd.DataFrame: Загруженный датафрейм
    """
    try:
        df = pd.read_csv(file_path)
        print(f"Загружено {len(df)} записей из {file_path}")
        return df
    except Exception as e:
        raise Exception(f"Ошибка загрузки данных: {e}")

def get_schema_for_prompt(df):
    """
    Получает информацию о схеме данных для использования в промпте LLM.
    
    Args:
        df (pd.DataFrame): Датафрейм для анализа
        
    Returns:
        str: Форматированная информация о схеме
    """
    schema_text = ""
    
    for col in df.columns:
        dtype = str(df[col].dtype)
        schema_text += f"- {col} ({dtype})"
        
        # Для категориальных колонок добавляем уникальные значения
        if df[col].dtype == 'object':
            unique_vals = df[col].unique().tolist()
            if len(unique_vals) < 20:  # Показываем только если разумное количество
                unique_vals_str = ", ".join([f"'{val}'" for val in unique_vals])
                schema_text += f"\n  Возможные значения: {unique_vals_str}"
        
        # Для числовых колонок добавляем диапазон
        elif df[col].dtype in ['int64', 'float64']:
            min_val = df[col].min()
            max_val = df[col].max()
            schema_text += f"\n  Диапазон: {min_val} до {max_val}"
            
        schema_text += "\n\n"
    
    return schema_text

def load_schema_from_file():
    """
    Загружает информацию о схеме из файла результатов EDA.
    
    Returns:
        dict: Информация о схеме
    """
    try:
        schema_path = os.path.join("data", "eda_results.json")
        with open(schema_path, 'r') as f:
            data = json.load(f)
            return data['schema']
    except Exception as e:
        print(f"Ошибка загрузки схемы из файла: {e}")
        return None

def analyze_data(df):
    """
    Проводит первичный анализ данных.
    
    Args:
        df (pd.DataFrame): Датафрейм для анализа
        
    Returns:
        dict: Словарь с результатами анализа
    """
    results = {}
    
    # Сохраняем результаты для использования в промпте LLM
    results['schema'] = get_schema_info(df)
    
    # Анализ примеров вопросов из задания
    results['example_questions'] = analyze_example_questions(df)
    
    return results

def get_schema_info(df):
    """
    Получает информацию о схеме данных.
    
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
    payment_method_column = 'Payment_Method'
    crypto_value = 'Crypto'
    if 'Cryptocurrency' in df[payment_method_column].values:
        crypto_value = 'Cryptocurrency'
    
    crypto_earnings = df[df[payment_method_column] == crypto_value]['Earnings_USD'].mean()
    other_earnings = df[df[payment_method_column] != crypto_value]['Earnings_USD'].mean()
    difference = crypto_earnings - other_earnings
    percentage = (difference / other_earnings) * 100
    
    results['crypto_vs_other'] = {
        'crypto_earnings': float(crypto_earnings),
        'other_earnings': float(other_earnings),
        'difference': float(difference),
        'percentage': float(percentage)
    }
    
    # 2. Как распределяется доход фрилансеров в зависимости от региона проживания?
    region_earnings = df.groupby('Client_Region')['Earnings_USD'].agg(['mean', 'median', 'count']).reset_index()
    region_earnings = region_earnings.sort_values(by='mean', ascending=False)
    
    results['region_earnings'] = region_earnings.to_dict('records')
    
    # 3. Какой процент фрилансеров, считающих себя экспертами, выполнил менее 100 проектов?
    experts = df[df['Experience_Level'] == 'Expert']
    experts_less_than_100 = experts[experts['Job_Completed'] < 100]
    percentage = (len(experts_less_than_100) / len(experts)) * 100
    
    results['experts_less_than_100'] = {
        'total_experts': len(experts),
        'experts_less_than_100': len(experts_less_than_100),
        'percentage': float(percentage)
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
