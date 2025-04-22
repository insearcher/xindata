import os
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress
from dotenv import load_dotenv
from src.data import load_data
from src.pandas_agent import PandasAgentService

load_dotenv()

app = typer.Typer()
console = Console()


def display_welcome_banner():
    console.print(Panel.fit(
        "[bold blue]Система анализа данных о фрилансерах[/bold blue]\n"
        "Задавайте вопросы о данных фрилансеров на естественном языке",
        title="Добро пожаловать",
        border_style="blue"
    ))


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


def initialize_agent(df, verbose=False):
    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]Инициализация ИИ агента...", total=1)

            import time
            time.sleep(1)
            agent_service = PandasAgentService(df, model_name="gpt-4o-mini", verbose=verbose)
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


@app.command()
def interactive(
        data_file: str = typer.Option("data/freelancer_earnings_bd.csv", "--data", "-d", help="Путь к CSV файлу с данными"),
        save_results: bool = typer.Option(False, "--save", "-s", help="Сохранять результаты в файл"),
        verbose: bool = typer.Option(False, "--verbose", "-v", help="Включить подробное логгирование")
):
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[bold red]Ошибка:[/bold red] API ключ OpenAI не найден")
        console.print("Пожалуйста, установите переменную окружения OPENAI_API_KEY или создайте файл .env")
        raise typer.Exit(1)

    if verbose:
        console.print("[yellow]Режим подробного логгирования включен[/yellow]")

    display_welcome_banner()

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

    agent_service = initialize_agent(df, verbose)

    display_example_questions()

    console.print("\n[bold green]Готов к вопросам.[/bold green] Введите 'выход', 'quit' или 'q' для завершения сеанса.")
    console.print("Введите 'примеры' для просмотра примеров вопросов или 'помощь' для вывода списка команд.")

    history = []

    while True:
        user_query = Prompt.ask("\n[bold blue]>:[/bold blue]")

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
                    "\n".join([f"{i + 1}. {q}" for i, q in enumerate(history)]),
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

        history.append(user_query)

        console.print("Анализирую ваш запрос...")
        try:
            result = agent_service.process_query(user_query)

            if result.get("error"):
                console.print(f"[bold red]Ошибка:[/bold red] {result['error']}")
                continue

            console.print(f"Ответ: {result['answer']}")

            last_result = result["answer"]

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


if __name__ == "__main__":
    app()
