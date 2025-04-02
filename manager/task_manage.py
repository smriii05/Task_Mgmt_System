"""
Task-related operations such as creating, updating, and listing tasks.
"""
import uuid
from db.database import get_db

async def create_task(user_id: int, name: str, description: str):
    """
    Creates a new task in the `tasks` table with a unique ID, associated 
    with a user. It uses a transaction to ensure atomicity.

    Args:
        user_id (int): The user ID that the task is associated with.
        name (str): The name of the task to be created.
        description (str): The description of the task to be created.
    """
    # Ensure name and description are not empty
    if not isinstance(name, str) or not name.strip():
        print("Error: Task name cannot be empty.")
        return  

    if not isinstance(description, str) or not description.strip():
        print("Error: Task description cannot be empty.")
        return  
    task_id = str(uuid.uuid4())

    async with get_db() as cursor:
        # Start transaction
        await cursor.execute("START TRANSACTION")
        
        try:
            # Insert new task
            await cursor.execute(
                "INSERT INTO tasks (id, user_id, name, description) VALUES (%s, %s, %s, %s)", 
                (task_id, user_id, name.strip(), description.strip())
            )
            # Commit the transaction
            await cursor.execute("COMMIT")
            print(f"Task '{name}' created successfully with ID {task_id}!")
        except Exception as e:
            # Rollback in case of error
            await cursor.execute("ROLLBACK")
            print(f"Error occurred: {e}. Task creation rolled back.")



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

async def update_task(task_id: str, name: str, description: str):
    """
    Updates the name and/or description of a task in the `tasks` table. 
    Uses a transaction to ensure atomicity.
    If no value is provided for a field, it will retain its old value.

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
        # Start transaction
        await cursor.execute("START TRANSACTION")
        
        try:
            # Update the task
            await cursor.execute(query, values)
            # Commit the transaction
            await cursor.execute("COMMIT")
            print(f"Task {task_id} updated successfully.")
        except Exception as e:
            # Rollback in case of error
            await cursor.execute("ROLLBACK")
            print(f"Error occurred: {e}. Task update rolled back.")



async def delete_task(task_id: str):
    """
    Deletes a task from the `tasks` table by its ID. 
    Uses a transaction to ensure atomicity.

    Args:
        task_id (str): The ID of the task to delete.
    """
    async with get_db() as cursor:
        # Start transaction
        await cursor.execute("START TRANSACTION")
        
        try:
            # Delete the task
            await cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            # Commit the transaction
            await cursor.execute("COMMIT")
            print(f"Task {task_id} deleted")
        except Exception as e:
            # Rollback in case of error
            await cursor.execute("ROLLBACK")
            print(f"Error occurred: {e}. Task deletion rolled back.")


async def change_task_status(task_id: str, status: str):
    """
    Changes the status of a task (Active or Archive). 
    Uses a transaction to ensure atomicity.

    Args:
        task_id (str): The ID of the task whose status needs to be updated.
        status (str): The new status to assign to the task ('Active' or 'Archive').
    """
    async with get_db() as cursor:
        # Start transaction
        await cursor.execute("START TRANSACTION")
        
        try:
            # Update the task status
            await cursor.execute("UPDATE tasks SET status = %s WHERE id = %s", (status, task_id))
            # Commit the transaction
            await cursor.execute("COMMIT")
            print(f"Task {task_id} status updated to {status}")
        except Exception as e:
            # Rollback in case of error
            await cursor.execute("ROLLBACK")
            print(f"Error occurred: {e}. Task status update rolled back.")