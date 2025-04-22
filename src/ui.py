from rich.console import Console
from rich.panel import Panel

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


def display_help_message():
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


def display_history(history):
    if not history:
        console.print("[yellow]Нет предыдущих запросов в этой сессии[/yellow]")
    else:
        console.print(Panel.fit(
            "\n".join([f"{i + 1}. {q}" for i, q in enumerate(history)]),
            title="История запросов",
            border_style="yellow"
        ))


def display_error(message, exception=None):
    error_text = f"[bold red]Ошибка:[/bold red] {message}"
    if exception:
        error_text += f" ({str(exception)})"
    console.print(error_text)
