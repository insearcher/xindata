"""
Enhanced Command Line Interface (CLI) for Freelancer Data Analysis System
"""

import os
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

# Load environment variables from .env file
load_dotenv()

app = typer.Typer()
console = Console()

# Function to display welcome banner
def display_welcome_banner():
    console.print(Panel.fit(
        "[bold blue]Freelancer Data Analysis System[/bold blue]\n"
        "Ask questions about freelancer data in natural language",
        title="Welcome",
        border_style="blue"
    ))

# Function to display example questions
def display_example_questions():
    example_questions = [
        "Насколько выше доход у фрилансеров, принимающих оплату в криптовалюте, по сравнению с другими способами оплаты?",
        "Как распределяется доход фрилансеров в зависимости от региона проживания?",
        "Какой процент фрилансеров, считающих себя экспертами, выполнил менее 100 проектов?",
        "Какая категория работы имеет самый высокий средний доход?",
        "Существует ли корреляция между рейтингом клиента и доходом фрилансера?"
    ]
    
    console.print("\n[bold cyan]Example Questions:[/bold cyan]")
    for i, q in enumerate(example_questions, 1):
        console.print(f"[cyan]{i}.[/cyan] {q}")

# Function to check if file exists
def check_file_exists(file_path):
    if not os.path.exists(file_path):
        alternative_path = os.path.join("data", "freelancer_earnings_bd_100.csv")
        if os.path.exists(alternative_path):
            console.print(f"[yellow]Warning:[/yellow] File {file_path} not found, using test file {alternative_path}")
            return alternative_path
        else:
            console.print(f"[bold red]Error:[/bold red] Data file not found at {file_path}")
            console.print("Please download the dataset from: [link]https://www.kaggle.com/datasets/shohinurpervezshohan/freelancer-earnings-and-job-trends[/link]")
            console.print("and place it in the data/ directory")
            raise typer.Exit(1)
    return file_path

# Function to initialize the agent
def initialize_agent(df):
    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]Initializing AI agent...", total=1)
            # Add a small delay for visual effect
            import time
            time.sleep(1)
            agent_service = PandasAgentService(df, model_name="gpt-4o-mini")
            progress.update(task, advance=1)
        console.print("[green]✓[/green] AI agent initialized successfully")
        return agent_service
    except Exception as e:
        console.print(f"[bold red]Error initializing agent:[/bold red] {str(e)}")
        raise typer.Exit(1)

# Function to save result to file
def save_to_file(query, result, file_path="results.txt"):
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"\nQuery: {query}\n")
        f.write(f"Result: {result}\n")
        f.write("-" * 80 + "\n")
    console.print(f"[green]Result saved to {file_path}[/green]")

# Command to run the interactive CLI
@app.command()
def interactive(
    data_file: str = typer.Option("data/freelancer_earnings_bd.csv", "--data", "-d", help="Path to the CSV data file"),
    save_results: bool = typer.Option(False, "--save", "-s", help="Save results to a file")
):
    """
    Start an interactive session to analyze freelancer data.
    """
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[bold red]Error:[/bold red] OpenAI API key not found")
        console.print("Please set the OPENAI_API_KEY environment variable or create a .env file")
        raise typer.Exit(1)
    
    # Display welcome
    display_welcome_banner()
    
    # Check and load data file
    data_path = check_file_exists(data_file)
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Loading data...", total=1)
        try:
            df = load_data(data_path)
            progress.update(task, advance=1)
        except Exception as e:
            progress.stop()
            console.print(f"[bold red]Error loading data:[/bold red] {str(e)}")
            raise typer.Exit(1)
    
    console.print(f"[green]✓[/green] Loaded {len(df)} records from {data_path}")
    
    # Initialize agent
    agent_service = initialize_agent(df)
    
    # Display example questions
    display_example_questions()
    
    # Main interaction loop
    console.print("\n[bold green]Ready for questions.[/bold green] Type 'exit', 'quit', or 'q' to end the session.")
    console.print("Type 'examples' to see example questions again, or 'help' for more commands.")
    
    history = []
    
    while True:
        # Get user input
        user_query = Prompt.ask("\n[bold blue]>[/bold blue]")
        
        # Process special commands
        if user_query.lower() in ['exit', 'quit', 'q']:
            console.print("[bold]Thank you for using the Freelancer Data Analysis System. Goodbye![/bold]")
            break
        
        elif user_query.lower() == 'examples':
            display_example_questions()
            continue
        
        elif user_query.lower() == 'help':
            console.print(Panel.fit(
                "Available commands:\n"
                "- [bold]exit[/bold], [bold]quit[/bold], [bold]q[/bold]: Exit the program\n"
                "- [bold]examples[/bold]: Show example questions\n"
                "- [bold]help[/bold]: Show this help message\n"
                "- [bold]history[/bold]: Show your query history\n"
                "- [bold]save[/bold]: Save the last result to a file",
                title="Help",
                border_style="green"
            ))
            continue
        
        elif user_query.lower() == 'history':
            if not history:
                console.print("[yellow]No previous queries in this session[/yellow]")
            else:
                console.print(Panel.fit(
                    "\n".join([f"{i+1}. {q}" for i, q in enumerate(history)]),
                    title="Query History",
                    border_style="yellow"
                ))
            continue
        
        elif user_query.lower() == 'save' and history:
            if history and 'last_result' in locals():
                save_to_file(history[-1], last_result, "results.txt")
            else:
                console.print("[yellow]No results to save yet[/yellow]")
            continue
        
        # Add to history
        history.append(user_query)
        
        # Process the query
        console.print("[cyan]Analyzing your question...[/cyan]")
        try:
            with Progress() as progress:
                task = progress.add_task("[cyan]Processing...", total=1)
                result = agent_service.process_query(user_query)
                progress.update(task, advance=1)
            
            if result.get("error"):
                console.print(f"[bold red]Error:[/bold red] {result['error']}")
                continue
            
            # Display the result
            console.print("\n[bold green]Answer:[/bold green]")
            console.print(Panel(result["answer"], border_style="green"))
            
            # Store for potential saving
            last_result = result["answer"]
            
            # Offer to save the result if the option is enabled
            if save_results:
                save = Prompt.ask(
                    "[yellow]Save this result to file?[/yellow]",
                    choices=["y", "n"],
                    default="n"
                )
                if save.lower() == "y":
                    save_to_file(user_query, last_result)
                    
        except Exception as e:
            console.print(f"[bold red]Error processing query:[/bold red] {str(e)}")

# Command to run a single query
@app.command()
def query(
    question: str = typer.Argument(..., help="The question to ask about the data"),
    data_file: str = typer.Option("data/freelancer_earnings_bd.csv", "--data", "-d", help="Path to the CSV data file"),
    save_result: bool = typer.Option(False, "--save", "-s", help="Save result to a file")
):
    """
    Run a single query and exit.
    """
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[bold red]Error:[/bold red] OpenAI API key not found")
        console.print("Please set the OPENAI_API_KEY environment variable or create a .env file")
        raise typer.Exit(1)
    
    # Check and load data file
    data_path = check_file_exists(data_file)
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Loading data...", total=1)
        try:
            df = load_data(data_path)
            progress.update(task, advance=1)
        except Exception as e:
            progress.stop()
            console.print(f"[bold red]Error loading data:[/bold red] {str(e)}")
            raise typer.Exit(1)
    
    # Initialize agent
    agent_service = initialize_agent(df)
    
    # Process the query
    console.print(f"[cyan]Processing query:[/cyan] {question}")
    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]Analyzing...", total=1)
            result = agent_service.process_query(question)
            progress.update(task, advance=1)
        
        if result.get("error"):
            console.print(f"[bold red]Error:[/bold red] {result['error']}")
            raise typer.Exit(1)
        
        # Display the result
        console.print("\n[bold green]Answer:[/bold green]")
        console.print(Panel(result["answer"], border_style="green"))
        
        # Save the result if requested
        if save_result:
            save_to_file(question, result["answer"])
            
    except Exception as e:
        console.print(f"[bold red]Error processing query:[/bold red] {str(e)}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
