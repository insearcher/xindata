import typer
from dotenv import load_dotenv
from rich.prompt import Prompt

from src.app import (
    check_api_key, check_file_exists, load_data,
    initialize_agent, process_query, DEFAULT_DATA_PATH
)
from src.ui import (
    console, display_welcome_banner, display_example_questions,
    display_help_message, EXIT_COMMANDS,
    HELP_COMMANDS, EXAMPLES_COMMANDS
)

load_dotenv()

app = typer.Typer()


@app.command()
def interactive(
        data_file: str = typer.Option(DEFAULT_DATA_PATH, "--data", "-d", help="Путь к CSV файлу с данными"),
        verbose: bool = typer.Option(False, "--verbose", "-v", help="Включить подробное логгирование")
):
    """
    Запускает интерактивный режим анализа данных фрилансеров.

    Пользователь может задавать вопросы на естественном языке,
    и система будет их анализировать с помощью LLM.
    """
    if not check_api_key():
        raise typer.Exit(1)

    if verbose:
        console.print("[yellow]Режим подробного логгирования включен[/yellow]")

    display_welcome_banner()

    data_path = check_file_exists(data_file)
    if not data_path:
        raise typer.Exit(1)

    df = load_data(data_path)
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

        if user_query.lower() in EXIT_COMMANDS:
            console.print("[bold]Спасибо за использование системы анализа данных о фрилансерах. До свидания![/bold]")
            break
        elif user_query.lower() in EXAMPLES_COMMANDS:
            display_example_questions()
        elif user_query.lower() in HELP_COMMANDS:
            display_help_message()
        elif user_query.strip():
            process_query(agent_service, user_query)


if __name__ == "__main__":
    app()
