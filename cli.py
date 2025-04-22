import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt

from src.app import (
    check_api_key, check_file_exists, load_data_with_progress,
    initialize_agent, process_query
)
from src.ui import (
    display_welcome_banner, display_example_questions,
    display_help_message
)

load_dotenv()

app = typer.Typer()
console = Console()


@app.command()
def interactive(
        data_file: str = typer.Option("data/freelancer_earnings_bd.csv", "--data", "-d", help="Путь к CSV файлу с данными"),
        verbose: bool = typer.Option(False, "--verbose", "-v", help="Включить подробное логгирование")
):
    if not check_api_key():
        raise typer.Exit(1)

    if verbose:
        console.print("[yellow]Режим подробного логгирования включен[/yellow]")

    display_welcome_banner()

    data_path = check_file_exists(data_file)
    if not data_path:
        raise typer.Exit(1)

    df = load_data_with_progress(data_path)
    if df is None:
        raise typer.Exit(1)

    agent_service = initialize_agent(df, verbose)
    if agent_service is None:
        raise typer.Exit(1)

    display_example_questions()

    console.print("\n[bold green]Готов к вопросам.[/bold green] Введите 'выход', 'quit' или 'q' для завершения сеанса.")
    console.print("Введите 'примеры' для просмотра примеров вопросов или 'помощь' для вывода списка команд.")

    while True:
        user_query = Prompt.ask("\n[bold blue]>[/bold blue]")

        if user_query.lower() in ['выход', 'exit', 'quit', 'q']:
            console.print("[bold]Спасибо за использование системы анализа данных о фрилансерах. До свидания![/bold]")
            break
        elif user_query.lower() in ['примеры', 'examples']:
            display_example_questions()
        elif user_query.lower() in ['помощь', 'help']:
            display_help_message()
        elif user_query.strip():
            process_query(agent_service, user_query)


if __name__ == "__main__":
    app()
