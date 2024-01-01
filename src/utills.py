from enum import Enum
import sqlite3
import inquirer
from rich.table import Table


class Status(Enum):
    TODO = "todo"
    DOING = "doing"
    DONE = "done"


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


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
    status: str,
    difficulty: str,
    connection: sqlite3.Connection,
    cursor: sqlite3.Cursor,
) -> None:
    createTable(connection=connection, cursor=cursor)
    cursor.execute(
        "INSERT INTO project_ideas (name, description, status, difficulty) VALUES (?, ?, ?, ?)",
        (name, description, status, difficulty),
    )
    connection.commit()


def getTableRows(cursor: sqlite3.Cursor) -> list:
    createTable(connection=cursor.connection, cursor=cursor)
    cursor.execute("SELECT * FROM project_ideas")
    rows = cursor.fetchall()
    return rows


def getIdeaData() -> tuple:
    taskQuestions = [
        inquirer.Text(
            "name",
            message="Enter name of the project idea",
            validate=lambda _, x: x != "",
        ),
        inquirer.Text(
            "description",
            message="Enter description of the project idea",
        ),
        inquirer.List(
            "status",
            message="Select status of the project idea",
            choices=[s.value for s in Status],
        ),
        inquirer.List(
            "difficulty",
            message="Select difficulty of the project idea",
            choices=[d.value for d in Difficulty],
        ),
    ]
    taskAnswers = inquirer.prompt(taskQuestions)

    name, description, status, difficulty = (
        taskAnswers.get(k, None)
        for k in ["name", "description", "status", "difficulty"]
    )
    return name, description, status, difficulty


def renderIdeasTable(rows: list, console: object) -> None:
    if not rows:
        console.print("[red]No project ideas found[/]. Create one with 'add'")
        return

    t = Table("ID", "Name", "Description", "Status", "Difficulty")

    for row in rows:
        id, name, description, status, difficulty = row
        t.add_row(
            f"[bold]{id}[/]",
            f"{name.title()}",
            f"{description[0].upper() + description[1:]}"
            if description
            else "No description",
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


def editGivenProp(
    answer: dict, id: int, cursor: sqlite3.Cursor, connection: sqlite3.Connection
) -> None:
    if answer["property"] == "name":
        nameQuestions = [
            inquirer.Text(
                "name",
                message="Enter new name",
                validate=lambda _, x: x != "",
            ),
        ]
        nameAnswers = inquirer.prompt(nameQuestions)
        cursor.execute(
            "UPDATE project_ideas SET name=? WHERE id=?",
            (nameAnswers["name"], id),
        )
    elif answer["property"] == "description":
        descriptionQuestions = [
            inquirer.Text(
                "description",
                message="Enter new description",
            ),
        ]
        descriptionAnswers = inquirer.prompt(descriptionQuestions)
        cursor.execute(
            "UPDATE project_ideas SET description=? WHERE id=?",
            (descriptionAnswers["description"], id),
        )
    elif answer["property"] == "status":
        statusQuestions = [
            inquirer.List(
                "status",
                message="Select new status",
                choices=[s.value for s in Status],
            ),
        ]
        statusAnswers = inquirer.prompt(statusQuestions)
        cursor.execute(
            "UPDATE project_ideas SET status=? WHERE id=?",
            (statusAnswers["status"], id),
        )
    elif answer["property"] == "difficulty":
        difficultyQuestions = [
            inquirer.List(
                "difficulty",
                message="Select new difficulty",
                choices=[d.value for d in Difficulty],
            ),
        ]
        difficultyAnswers = inquirer.prompt(difficultyQuestions)
        cursor.execute(
            "UPDATE project_ideas SET difficulty=? WHERE id=?",
            (difficultyAnswers["difficulty"], id),
        )
    connection.commit()
