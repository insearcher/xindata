"""
Улучшенный интерфейс командной строки (CLI) для системы анализа данных о фрилансерах
"""

import os
import sys
import pandas as pd
import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Prompt
from rich.progress import Progress
from dotenv import load_dotenv
from src.data_analysis import load_data
from src.pandas_agent import PandasAgentService

# Загрузка переменных окружения из файла .env
load_dotenv()

app = typer.Typer()
console = Console()

# Функция для отображения приветственного баннера
def display_welcome_banner():
    console.print(Panel.fit(
        "[bold blue]Система анализа данных о фрилансерах[/bold blue]\n"
        "Задавайте вопросы о данных фрилансеров на естественном языке",
        title="Добро пожаловать",
        border_style="blue"
    ))

# Функция для отображения примеров вопросов
def display_example_questions():
    example_questions = [
        "Насколько выше доход у фрилансеров, принимающих оплату в криптовалюте, по сравнению с другими способами оплаты?",
        "Как распределяется доход фрилансеров в зависимости от региона проживания?",
        "Какой процент фрилансеров, считающих себя экспертами, выполнил менее 100 проектов?",
        "Какая категория работы имеет самый высокий средний доход?",
        "Существует ли корреляция между рейтингом клиента и доходом фрилансера?"
    ]
    
    console.print("\n[bold cyan]Примеры вопросов:[/bold cyan]")
    for i, q in enumerate(example_questions, 1):
        console.print(f"[cyan]{i}.[/cyan] {q}")

# Функция для проверки существования файла
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
            raise typer.Exit(1)
    return file_path

# Функция для инициализации агента
def initialize_agent(df):
    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]Инициализация ИИ агента...", total=1)
            # Небольшая задержка для визуального эффекта
            import time
            time.sleep(1)
            agent_service = PandasAgentService(df, model_name="gpt-4o-mini")
            progress.update(task, advance=1)
        console.print("[green]✓[/green] ИИ агент успешно инициализирован")
        return agent_service
    except Exception as e:
        console.print(f"[bold red]Ошибка инициализации агента:[/bold red] {str(e)}")
        raise typer.Exit(1)

# Функция для сохранения результата в файл
def save_to_file(query, result, file_path="results.txt"):
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"\nЗапрос: {query}\n")
        f.write(f"Результат: {result}\n")
        f.write("-" * 80 + "\n")
    console.print(f"[green]Результат сохранен в {file_path}[/green]")

# Команда для запуска интерактивного CLI
@app.command()
def interactive(
    data_file: str = typer.Option("data/freelancer_earnings_bd.csv", "--data", "-d", help="Путь к CSV файлу с данными"),
    save_results: bool = typer.Option(False, "--save", "-s", help="Сохранять результаты в файл")
):
    """
    Запуск интерактивного режима для анализа данных о фрилансерах.
    """
    # Проверка наличия API ключа
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[bold red]Ошибка:[/bold red] API ключ OpenAI не найден")
        console.print("Пожалуйста, установите переменную окружения OPENAI_API_KEY или создайте файл .env")
        raise typer.Exit(1)
    
    # Отображение приветствия
    display_welcome_banner()
    
    # Проверка и загрузка файла данных
    data_path = check_file_exists(data_file)
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Загрузка данных...", total=1)
        try:
            df = load_data(data_path)
            progress.update(task, advance=1)
        except Exception as e:
            progress.stop()
            console.print(f"[bold red]Ошибка загрузки данных:[/bold red] {str(e)}")
            raise typer.Exit(1)
    
    console.print(f"[green]✓[/green] Загружено {len(df)} записей из {data_path}")
    
    # Инициализация агента
    agent_service = initialize_agent(df)
    
    # Отображение примеров вопросов
    display_example_questions()
    
    # Основной цикл взаимодействия
    console.print("\n[bold green]Готов к вопросам.[/bold green] Введите 'выход', 'quit' или 'q' для завершения сеанса.")
    console.print("Введите 'примеры' для просмотра примеров вопросов или 'помощь' для вывода списка команд.")
    
    history = []
    
    while True:
        # Получение ввода пользователя
        user_query = Prompt.ask("\n[bold blue]>:[/bold blue]")
        
        # Обработка специальных команд
        if user_query.lower() in ['выход', 'exit', 'quit', 'q']:
            console.print("[bold]Спасибо за использование системы анализа данных о фрилансерах. До свидания![/bold]")
            break
        
        elif user_query.lower() in ['примеры', 'examples']:
            display_example_questions()
            continue
        
        elif user_query.lower() in ['помощь', 'help']:
            console.print(Panel.fit(
                "Доступные команды:\n"
                "- [bold]выход[/bold], [bold]exit[/bold], [bold]quit[/bold], [bold]q[/bold]: Выход из программы\n"
                "- [bold]примеры[/bold], [bold]examples[/bold]: Показать примеры вопросов\n"
                "- [bold]помощь[/bold], [bold]help[/bold]: Показать это сообщение\n"
                "- [bold]история[/bold], [bold]history[/bold]: Показать историю ваших запросов\n"
                "- [bold]сохранить[/bold], [bold]save[/bold]: Сохранить последний результат в файл",
                title="Помощь",
                border_style="green"
            ))
            continue
        
        elif user_query.lower() in ['история', 'history']:
            if not history:
                console.print("[yellow]Нет предыдущих запросов в этой сессии[/yellow]")
            else:
                console.print(Panel.fit(
                    "\n".join([f"{i+1}. {q}" for i, q in enumerate(history)]),
                    title="История запросов",
                    border_style="yellow"
                ))
            continue
        
        elif user_query.lower() in ['сохранить', 'save'] and history:
            if history and 'last_result' in locals():
                save_to_file(history[-1], last_result, "results.txt")
            else:
                console.print("[yellow]Пока нет результатов для сохранения[/yellow]")
            continue
        
        # Добавление в историю
        history.append(user_query)
        
        # Обработка запроса
        console.print("Анализирую ваш запрос...")
        try:
            # Отключаем вывод лишней информации
            result = agent_service.process_query(user_query)
            
            if result.get("error"):
                console.print(f"[bold red]Ошибка:[/bold red] {result['error']}")
                continue
            
            # Отображение результата в нужном формате
            console.print(f"Ответ: {result['answer']}")
            
            # Сохранение для возможного использования
            last_result = result["answer"]
            
            # Предложение сохранить результат, если опция включена
            if save_results:
                save = Prompt.ask(
                    "[yellow]Сохранить этот результат в файл?[/yellow]",
                    choices=["y", "n"],
                    default="n"
                )
                if save.lower() == "y":
                    save_to_file(user_query, last_result)
                    
        except Exception as e:
            console.print(f"[bold red]Ошибка обработки запроса:[/bold red] {str(e)}")

# Команда для выполнения одиночного запроса
@app.command()
def query(
    question: str = typer.Argument(..., help="Вопрос о данных"),
    data_file: str = typer.Option("data/freelancer_earnings_bd.csv", "--data", "-d", help="Путь к CSV файлу с данными"),
    save_result: bool = typer.Option(False, "--save", "-s", help="Сохранить результат в файл")
):
    """
    Выполнение одиночного запроса и выход.
    """
    # Проверка наличия API ключа
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[bold red]Ошибка:[/bold red] API ключ OpenAI не найден")
        console.print("Пожалуйста, установите переменную окружения OPENAI_API_KEY или создайте файл .env")
        raise typer.Exit(1)
    
    # Проверка и загрузка файла данных
    data_path = check_file_exists(data_file)
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Загрузка данных...", total=1)
        try:
            df = load_data(data_path)
            progress.update(task, advance=1)
        except Exception as e:
            progress.stop()
            console.print(f"[bold red]Ошибка загрузки данных:[/bold red] {str(e)}")
            raise typer.Exit(1)
    
    # Инициализация агента
    agent_service = initialize_agent(df)
    
    # Обработка запроса
    console.print(f"Анализирую запрос: {question}")
    try:
        # Отключаем отображение промежуточных шагов
        result = agent_service.process_query(question)
        
        if result.get("error"):
            console.print(f"[bold red]Ошибка:[/bold red] {result['error']}")
            raise typer.Exit(1)
        
        # Отображение результата в нужном формате
        console.print(f"\nОтвет: {result['answer']}")
        
        # Сохранение результата, если запрошено
        if save_result:
            save_to_file(question, result["answer"])
            
    except Exception as e:
        console.print(f"[bold red]Ошибка обработки запроса:[/bold red] {str(e)}")
        raise typer.Exit(1)

# Запуск интерактивного режима по умолчанию при отсутствии аргументов
def main():
    """
    Основная функция для запуска приложения.
    Запускает интерактивный режим, если не указаны аргументы.
    """
    if len(sys.argv) == 1:
        interactive()
    else:
        app()

if __name__ == "__main__":
    main()
