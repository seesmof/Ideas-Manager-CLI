from os import path
import inquirer
from rich.markdown import Markdown as md
from rich.console import Console
from rich.traceback import install
from click_shell import shell
import sqlite3

from utills import (
    addTask,
    editGivenProp,
    getIdeaData,
    getTableRows,
    renderIdeasTable,
)

install()
console = Console()

currentDir = path.dirname(path.abspath(__file__))
databasePath = path.join(currentDir, "..", "data", "project_ideas.db")
connection = sqlite3.connect(databasePath)
cursor = connection.cursor()


@shell(
    prompt="> ",
)
def pm_shell():
    console.print(
        "Welcome to [bold]Project Ideas Manager[/]!\nEnter 'help' for list of commands"
    )


@pm_shell.command()
def help():
    console.print(
        md(
            """
This CLI tool helps you manage your project ideas. You can use it to add, remove and edit your project ideas as well as assign them different properties like `status` and `difficulty`.

Here is a list of all commands:

- help: See this list
- add: Add a new project idea
- remove: Remove a project idea
- edit: Edit a project idea
- show: Show all project ideas
- exit: Exit the shell
"""
        )
    )


@pm_shell.command()
def add():
    name, description, status, difficulty = getIdeaData()
    addTask(
        name=name,
        description=description,
        status=status,
        difficulty=difficulty,
        connection=connection,
        cursor=cursor,
    )
    renderIdeasTable(rows=getTableRows(cursor=cursor), console=console)


@pm_shell.command()
def remove():
    renderIdeasTable(rows=getTableRows(cursor=cursor), console=console)

    idQuestions = [
        inquirer.Text(
            "id",
            message="Enter ID of the project idea you want to remove",
            validate=lambda _, x: x != "" and x.isdigit(),
        ),
    ]
    idAnswers = inquirer.prompt(idQuestions)
    ideaId = int(idAnswers["id"])

    try:
        cursor.execute("DELETE FROM project_ideas WHERE id = ?", (ideaId,))
        connection.commit()
        console.print(f"[green]Removed task with ID {ideaId}[/]")
    except Exception as e:
        console.print(f"[red]Failed to remove task: {e}[/]")


@pm_shell.command()
def edit():
    renderIdeasTable(rows=getTableRows(cursor=cursor), console=console)

    idQuestions = [
        inquirer.Text(
            "id",
            message="Enter ID of the project idea you want to edit",
            validate=lambda _, x: x != "" and x.isdigit(),
        )
    ]
    idAnswers = inquirer.prompt(idQuestions)
    ideaId = int(idAnswers["id"])

    propertySelectQuestions = [
        inquirer.List(
            "property",
            message="Select property to edit",
            choices=["name", "description", "status", "difficulty"],
        )
    ]
    propertySelectAnswers = inquirer.prompt(propertySelectQuestions)

    editGivenProp(
        answer=propertySelectAnswers, id=ideaId, cursor=cursor, connection=connection
    )
    renderIdeasTable(rows=getTableRows(cursor=cursor), console=console)


@pm_shell.command()
def show():
    renderIdeasTable(rows=getTableRows(cursor=cursor), console=console)


if __name__ == "__main__":
    pm_shell()
