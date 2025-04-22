import os
from typing import Optional

import pandas as pd
from rich.console import Console

from src.pandas_agent import PandasAgentService, DEFAULT_MODEL

# Константы
DEFAULT_DATA_PATH = "data/freelancer_earnings_bd.csv"
ALTERNATIVE_DATA_PATH = "data/freelancer_earnings_bd_100.csv"

console = Console()


def check_api_key() -> bool:
    """
    Проверяет наличие API ключа OpenAI в переменных окружения.

    Returns:
        bool: True если ключ найден, False если нет
    """
    if not os.getenv("OPENAI_API_KEY"):
        from src.ui import display_error
        display_error("API ключ OpenAI не найден")
        console.print("Пожалуйста, установите переменную окружения OPENAI_API_KEY или создайте файл .env")
        return False
    return True


def check_file_exists(file_path: str) -> Optional[str]:
    """
    Проверяет существование файла данных и предлагает альтернативу при необходимости.

    Args:
        file_path: Путь к файлу для проверки

    Returns:
        Путь к найденному файлу или None если файл не найден
    """
    from src.ui import display_error

    if not os.path.exists(file_path):
        if os.path.exists(ALTERNATIVE_DATA_PATH):
            console.print(f"[yellow]Предупреждение:[/yellow] Файл {file_path} не найден, используется тестовый файл {ALTERNATIVE_DATA_PATH}")
            return ALTERNATIVE_DATA_PATH
        else:
            display_error(f"Файл с данными не найден по пути {file_path}")
            console.print("Пожалуйста, скачайте набор данных по ссылке: [link]https://www.kaggle.com/datasets/shohinurpervezshohan/freelancer-earnings-and-job-trends[/link]")
            console.print("и поместите его в директорию data/")
            return None
    return file_path


def load_data(data_path: str) -> Optional[pd.DataFrame]:
    """
    Загружает данные из CSV файла.

    Args:
        data_path: Путь к CSV файлу

    Returns:
        DataFrame с загруженными данными или None при ошибке
    """
    try:
        df = pd.read_csv(data_path)
        console.print(f"[green]✓[/green] Загружено {len(df)} записей из {data_path}")
        return df
    except Exception as e:
        from src.ui import display_error
        display_error("Ошибка загрузки данных", e)
        return None


def initialize_agent(df: pd.DataFrame, verbose: bool = False) -> Optional[PandasAgentService]:
    """
    Инициализирует агента для анализа данных.

    Args:
        df: DataFrame для анализа
        verbose: Включить подробный вывод

    Returns:
        Инициализированный агент или None при ошибке
    """
    try:
        agent_service = PandasAgentService(df, model_name=DEFAULT_MODEL, verbose=verbose)
        console.print("[green]✓[/green] ИИ агент успешно инициализирован")
        return agent_service
    except Exception as e:
        from src.ui import display_error
        display_error("Ошибка инициализации агента", e)
        return None


def process_query(agent_service: PandasAgentService, query: str) -> Optional[str]:
    """
    Обрабатывает запрос пользователя и выводит результат.

    Args:
        agent_service: Агент для обработки запроса
        query: Запрос пользователя

    Returns:
        Ответ на запрос или None при ошибке
    """
    from src.ui import display_error

    console.print("Анализирую ваш запрос...")
    try:
        result = agent_service.process_query(query)
        if result.get("error"):
            display_error(result['error'])
            return None
        console.print(f"Ответ: {result['answer']}")
        return result["answer"]
    except Exception as e:
        display_error("Ошибка обработки запроса", e)
        return None
