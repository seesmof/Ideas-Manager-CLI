from os import path
from rich.markdown import Markdown as md
from rich.console import Console
from rich.traceback import install
from click_shell import shell
import sqlite3

from utills import (
    addTask,
    createTable,
    getNewIdeaData,
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
        md("Welcome to _Project Ideas Manager_!\n\nEnter `help` for list of commands")
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
    name, description, status, difficulty = getNewIdeaData(console=console)

    if not name:
        console.print("[red]Name cannot be empty[/]")
        return

    createTable(connection=connection, cursor=cursor)
    addTask(
        name=name,
        description=description,
        status=status,
        difficulty=difficulty,
        connection=connection,
        cursor=cursor,
    )

    console.print("[green]Task added successfully[/]")


@pm_shell.command()
def remove():
    rows = getTableRows(cursor=cursor, console=console)
    renderIdeasTable(rows=rows, console=console)
    try:
        ideaId = int(input("Enter the ID of the project idea you want to remove: "))
    except Exception:
        console.print("[red]Invalid ID[/]")
        return

    try:
        cursor.execute("DELETE FROM project_ideas WHERE id = ?", (ideaId,))
        connection.commit()
        console.print("[green]Task removed successfully[/]")
    except Exception as e:
        console.print(f"[red]Failed to remove task: {e}[/]")


@pm_shell.command()
def edit():
    rows = getTableRows(cursor=cursor, console=console)
    if not rows:
        console.print("[red]No project ideas found[/]. Create one with 'add'")
        return
    renderIdeasTable(rows=rows, console=console)

    try:
        ideaId = int(input("Enter the ID of the project idea you want to edit: "))
    except Exception:
        console.print("[red]Invalid ID[/]")
        return

    name, description, status, difficulty = getNewIdeaData(console=console)

    if not name:
        console.print("[red]Name cannot be empty[/]")
        return

    sqlQuery = """
        UPDATE project_ideas
        SET name = ?, description = ?, status = ?, difficulty = ?
        WHERE id = ?
    """

    with connection:
        cursor.execute(
            sqlQuery, (name, description, status.value, difficulty.value, ideaId)
        )

    console.print("[green]Task edited successfully[/]")


@pm_shell.command()
def show():
    rows = getTableRows(cursor=cursor, console=console)
    if not rows:
        return

    renderIdeasTable(rows=rows, console=console)


if __name__ == "__main__":
    pm_shell()
