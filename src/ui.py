from typing import Optional

from rich.console import Console
from rich.panel import Panel

console = Console()

# Константы
EXIT_COMMANDS = ['выход', 'exit', 'quit', 'q']
HELP_COMMANDS = ['помощь', 'help']
EXAMPLES_COMMANDS = ['примеры', 'examples']

# Пример вопросов для системы
EXAMPLE_QUESTIONS = [
    "Насколько выше доход у фрилансеров, принимающих оплату в криптовалюте, по сравнению с другими способами оплаты?",
    "Как распределяется доход фрилансеров в зависимости от региона проживания?",
    "Какой процент фрилансеров, считающих себя экспертами, выполнил менее 100 проектов?",
    "Какая категория работы имеет самый высокий средний доход?",
    "Существует ли корреляция между рейтингом клиента и доходом фрилансера?"
]


def display_welcome_banner() -> None:
    """Отображает приветственный баннер при запуске приложения"""
    console.print(Panel.fit(
        "[bold blue]Система анализа данных о фрилансерах[/bold blue]\n"
        "Задавайте вопросы о данных фрилансеров на естественном языке",
        title="Добро пожаловать",
        border_style="blue"
    ))


def display_example_questions() -> None:
    """Отображает примеры вопросов, которые можно задать системе"""
    console.print("\n[bold cyan]Примеры вопросов:[/bold cyan]")
    for i, q in enumerate(EXAMPLE_QUESTIONS, 1):
        console.print(f"[cyan]{i}.[/cyan] {q}")


def display_help_message() -> None:
    """Отображает справочное сообщение с доступными командами"""
    console.print(Panel.fit(
        "Доступные команды:\n"
        f"- [bold]{', '.join(EXIT_COMMANDS)}[/bold]: Выход из программы\n"
        f"- [bold]{', '.join(EXAMPLES_COMMANDS)}[/bold]: Показать примеры вопросов\n"
        f"- [bold]{', '.join(HELP_COMMANDS)}[/bold]: Показать это сообщение",
        title="Помощь",
        border_style="green"
    ))


def display_error(message: str, exception: Optional[Exception] = None) -> None:
    """
    Отображает сообщение об ошибке в консоли.

    Args:
        message: Текст сообщения об ошибке
        exception: Исключение, которое вызвало ошибку (если есть)
    """
    error_text = f"[bold red]Ошибка:[/bold red] {message}"
    if exception:
        error_text += f" ({str(exception)})"
    console.print(error_text)
