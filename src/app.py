import os

import pandas as pd
from rich.console import Console

from src.pandas_agent import PandasAgentService

console = Console()


def check_api_key():
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[bold red]Ошибка:[/bold red] API ключ OpenAI не найден")
        console.print("Пожалуйста, установите переменную окружения OPENAI_API_KEY или создайте файл .env")
        return False
    return True


def check_file_exists(file_path):
    if not os.path.exists(file_path):
        alternative_path = os.path.join("data", "freelancer_earnings_bd_100.csv")
        if os.path.exists(alternative_path):
            console.print(f"[yellow]Предупреждение:[/yellow] Файл {file_path} не найден, используется тестовый файл {alternative_path}")
            return alternative_path
        else:
            console.print(f"[bold red]Ошибка:[/bold red] Файл с данными не найден по пути {file_path}")
            console.print("Пожалуйста, скачайте набор данных по ссылке: [link]https://www.kaggle.com/datasets/shohinurpervezshohan/freelancer-earnings-and-job-trends[/link]")
            console.print("и поместите его в директорию data/")
            return None
    return file_path


def load_data_with_progress(data_path):
    try:
        df = pd.read_csv(data_path)
        console.print(f"[green]✓[/green] Загружено {len(df)} записей из {data_path}")
        return df
    except Exception as e:
        console.print(f"[bold red]Ошибка загрузки данных:[/bold red] {str(e)}")
        return None


def initialize_agent(df, verbose=False):
    try:
        agent_service = PandasAgentService(df, model_name="gpt-4o-mini", verbose=verbose)
        console.print("[green]✓[/green] ИИ агент успешно инициализирован")
        return agent_service
    except Exception as e:
        console.print(f"[bold red]Ошибка инициализации агента:[/bold red] {str(e)}")
        return None


def process_query(agent_service, query):
    console.print("Анализирую ваш запрос...")
    try:
        result = agent_service.process_query(query)
        if result.get("error"):
            console.print(f"[bold red]Ошибка:[/bold red] {result['error']}")
            return None
        console.print(f"Ответ: {result['answer']}")
        return result["answer"]
    except Exception as e:
        console.print(f"[bold red]Ошибка обработки запроса:[/bold red] {str(e)}")
        return None
