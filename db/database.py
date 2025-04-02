import aiomysql
import asyncio
import uuid
from contextlib import asynccontextmanager

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "db": "task_manager",
    "port": 3306,
}

@asynccontextmanager
async def get_db():
    """
    Asynchronous context manager for connecting to the MySQL database.
    Provides a cursor for executing queries, and automatically commits 
    changes when the context exits.

    Yields:
        cursor: Database cursor for executing SQL queries.
    """
    conn = await aiomysql.connect(**DB_CONFIG)
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            yield cursor
        await conn.commit()
    finally:
        conn.close()

async def init_db():
    """
    Initializes the database by creating the `users` and `tasks` tables 
    if they do not already exist.
    """
    async with get_db() as cursor:
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL
            )AUTO_INCREMENT = 101;
        """)
        
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id VARCHAR(36) PRIMARY KEY,
                user_id INT,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                status ENUM('Active', 'Archive') DEFAULT 'Active',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        print("Database initialized successfully!")

async def create_user(username: str):
    async with get_db() as cursor:
        await cursor.execute("INSERT INTO users (username) VALUES (%s)", (username,))
        await cursor.execute("SELECT LAST_INSERT_ID()")  # Get the last inserted ID
        user_id = await cursor.fetchone()
    
    user_id = user_id["LAST_INSERT_ID()"]
    print(f"User {username} created successfully with ID {user_id}")
    return user_id 


async def create_task(user_id: int, name: str, description: str = ""):
    """
    Creates a new task in the `tasks` table with a unique ID, associated 
    with a user.

    Args:
        user_id (int): The user ID that the task is associated with.
        name (str): The name/description of the task to be created.
    """
    task_id = str(uuid.uuid4())
    async with get_db() as cursor:
        await cursor.execute(
            "INSERT INTO tasks (id, user_id, name,description) VALUES (%s, %s, %s, %s)", 
            (task_id, user_id, name, description)
        )
    print(f"Task '{name}' created successfully with ID {task_id}!")


async def list_tasks(user_id: int):
    """
    Lists all active tasks for a given user.

    Args:
        user_id (int): The user ID for which tasks should be listed.

    Returns:
        list: A list of dictionaries containing task information.
    """
    async with get_db() as cursor:
        await cursor.execute("SELECT * FROM tasks WHERE user_id = %s AND status = 'Active'", (user_id,))
        tasks = await cursor.fetchall()
        return tasks

async def get_task(task_id: str):
    """
    Retrieves a specific task from the `tasks` table by its ID.

    Args:
        task_id (str): The unique ID of the task to retrieve.

    Returns:
        dict: A dictionary containing task information.
    """
    async with get_db() as cursor:
        await cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
        task = await cursor.fetchone()
        return task

async def update_task(task_id: str, name: str= "", description: str= ""):
    """
    Updates the name and/or description of a task in the `tasks` table.

    Args:
        task_id (str): The ID of the task to update.
        name (str, optional): The new name of the task. Defaults to None.
        description (str, optional): The new description of the task. Defaults to None.
    """
    update_fields = []
    values = []

    if name is not None:
        update_fields.append("name = %s")
        values.append(name)
    
    if description is not None:
        update_fields.append("description = %s")
        values.append(description)

    if not update_fields:
        print("No updates provided.")
        return

    values.append(task_id)
    
    query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = %s"

    async with get_db() as cursor:
        await cursor.execute(query, values)
    
    print(f"Task {task_id} updated successfully.")


async def delete_task(task_id: str):
    """
    Deletes a task from the `tasks` table by its ID.

    Args:
        task_id (str): The ID of the task to delete.
    """
    async with get_db() as cursor:
        await cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    print(f"Task {task_id} deleted")

async def change_task_status(task_id: str, status: str):
    """
    Changes the status of a task (Active or Archive).

    Args:
        task_id (str): The ID of the task whose status needs to be updated.
        status (str): The new status to assign to the task ('Active' or 'Archive').
    """
    async with get_db() as cursor:
        await cursor.execute("UPDATE tasks SET status = %s WHERE id = %s", (status, task_id))
    print(f"Task {task_id} status updated to {status}")

if __name__ == "__main__":
    asyncio.run(init_db())
