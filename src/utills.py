from enum import Enum
import sqlite3
from rich.table import Table


class Status(Enum):
    TODO = "todo"
    DOING = "doing"
    DONE = "done"


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


def getTableRows(cursor: sqlite3.Cursor, console: object) -> list:
    createTable(connection=cursor.connection, cursor=cursor)
    cursor.execute("SELECT * FROM project_ideas")
    rows = cursor.fetchall()
    if not rows:
        console.print("[red]No project ideas found[/]. Create one with 'add'")
        return []
    return rows


def createTable(cursor: sqlite3.Cursor, connection: sqlite3.Connection) -> None:
    query = """
    CREATE TABLE IF NOT EXISTS project_ideas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        status TEXT,
        difficulty TEXT
    )
    """
    cursor.execute(query)
    connection.commit()


def addTask(
    name: str,
    description: str,
    status: Status,
    difficulty: Difficulty,
    connection: sqlite3.Connection,
    cursor: sqlite3.Cursor,
) -> None:
    cursor.execute(
        "INSERT INTO project_ideas (name, description, status, difficulty) VALUES (?, ?, ?, ?)",
        (name, description, status.value, difficulty.value),
    )
    connection.commit()


def getIdeaData(console: object) -> tuple:
    console.print()

    name = input("Project Name - Required\n: ")
    description = input("Project Description - Can be empty\n: ")
    status = input("Project Status - todo | doing | done. Default is todo\n: ")
    difficulty = input("Project Difficulty - easy | medium | hard. Default is easy\n: ")

    console.print()

    name = name.title() if name else None
    description = description if description else None

    status = (
        Status(status)
        if status.lower() in [s.value.lower() for s in Status]
        else Status.TODO
    )
    difficulty = (
        Difficulty(difficulty)
        if difficulty.lower() in [d.value.lower() for d in Difficulty]
        else Difficulty.EASY
    )

    return name, description, status, difficulty


def renderIdeasTable(rows: list, console: object) -> None:
    t = Table("ID", "Name", "Description", "Status", "Difficulty")

    for row in rows:
        id, name, description, status, difficulty = row
        t.add_row(
            f"[bold]{id}[/]",
            f"{name}",
            f"{description[0].upper() + description[1:]}" if description else "",
            f"[blue]{status.title()}[/]"
            if status == "todo"
            else f"[yellow]{status.title()}[/]"
            if status == "doing"
            else f"[green]{status.title()}[/]",
            f"[green]{difficulty.title()}[/]"
            if difficulty == "easy"
            else f"[yellow]{difficulty.title()}[/]"
            if difficulty == "medium"
            else f"[red]{difficulty.title()}[/]",
        )

    console.print(t)
