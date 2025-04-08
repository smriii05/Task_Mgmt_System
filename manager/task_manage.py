"""
Task-related operations such as creating, updating, and listing tasks.
"""
import uuid
from db.database import get_db
from exception_handler import  BadRequestError, NotFoundError, TaskOperationException, InternalServerError

async def create_task(user_id: int, name: str, description: str):
    """
    Creates a new task in the `tasks` table with a unique ID, associated 
    with a user.

    Args:
        user_id (int): The user ID that the task is associated with.
        name (str): The name of the task to be created.
        description (str): The description of the task to be created.
    """
    task_id = str(uuid.uuid4())

    async with get_db() as cursor:
        try:
            # Check if the user exists in the users table
            await cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
            user = await cursor.fetchone()

            if not user:
                raise NotFoundError(f"User with {user_id} does not exist.")
            
            if isinstance(user_id, str):
                raise BadRequestError(f"Invalid user id: '{user_id}'. User ID should be an integer, not a string.")
            
            # Check for duplicate task names for the user (if required)
            await cursor.execute("SELECT id FROM tasks WHERE user_id = %s AND name = %s", (user_id, name.strip()))
            existing_task = await cursor.fetchone()

            if existing_task:
                raise TaskOperationException("Task with this name already exists for the user", "409 Conflict")
            
            if not name.strip():
                raise BadRequestError("Task name cannot be empty")
            
            # Insert new task if the user exists
            await cursor.execute(
                "INSERT INTO tasks (id, user_id, name, description) VALUES (%s, %s, %s, %s)", 
                (task_id, user_id, name.strip(), description.strip())
            )

            print(f"Task '{name}' created successfully with ID {task_id}!")
            return task_id

        except NotFoundError as e:
            raise
        except TaskOperationException as e:
            raise
        except BadRequestError as e:
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")


async def list_tasks(user_id: int):
    """
    Lists all active tasks for a given user.

    Args:
        user_id (int): The user ID for which tasks should be listed.

    Returns:
        list: A list of dictionaries containing task information.
    """
    async with get_db() as cursor:
        try:
            # Check if the user exists
            await cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = await cursor.fetchone()

            if not user_id:
                raise NotFoundError(f"User with ID {user_id} does not exist.")

            await cursor.execute("SELECT * FROM tasks WHERE user_id = %s", (user_id,))
            tasks = await cursor.fetchall()

            if not tasks:
                raise NotFoundError("No tasks found for this user.")
            
            return tasks
   
        except NotFoundError as e:
            raise


async def get_task(task_id: str):
    """
    Retrieves a specific task from the `tasks` table by its ID.

    Args:
        task_id (str): The unique ID of the task to retrieve.

    Returns:
        dict: A dictionary containing task information.
    """
    async with get_db() as cursor:
        try:
            uuid.UUID(task_id)

            await cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            task = await cursor.fetchone()
        
            if not task:
                raise NotFoundError(f"Task with {task_id} couldn't be found.")
            
            return task
        
        except ValueError:
            raise TaskOperationException("Invalid Task ID format.", "400 Bad Request")
        
        except NotFoundError as e:
            raise
        
        except TaskOperationException as e:
            raise


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

    if name:
        update_fields.append("name = %s")
        values.append(name)
    
    if description:
        update_fields.append("description = %s")
        values.append(description)

    values.append(task_id)
    query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = %s"

    async with get_db() as cursor:
        try:
            # Start transaction
            await cursor.execute("START TRANSACTION")
            
            uuid.UUID(task_id)

            # Check if task exists
            await cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            task = await cursor.fetchone()
        
            if not task:
                raise NotFoundError(f"Task with ID {task_id} couldn't be found.")
            
            # Update the task
            await cursor.execute(query, values)
            # Commit the transaction
            await cursor.execute("COMMIT")
            print(f"Task {task_id} updated successfully.")
        
    
        except NotFoundError as e:
            # Rollback if task is not found
            await cursor.execute("ROLLBACK")
            raise

        except ValueError:
            raise TaskOperationException("Invalid Task ID format.", "400 Bad Request")

        except Exception as e:
            # Rollback in case of any unexpected errors
            await cursor.execute("ROLLBACK")
            print(f"Error occurred: {e}. Task update rolled back.")

    if not update_fields:
        print("No updates provided.")
        return


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
            # Check if task exists
            await cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            task = await cursor.fetchone()

            if not task:
                raise NotFoundError(f"Task with {task_id} couldn't be found. Enter an existing Task ID")
            
            # Delete the task
            await cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            # Commit the transaction
            await cursor.execute("COMMIT")
            print(f"Task {task_id} deleted")
        
        except NotFoundError as e:
            raise
        except InternalServerError as e:
            raise
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
            uuid.UUID(task_id)

            # Check if task exists
            await cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            task = await cursor.fetchone()

            if not task:
                raise NotFoundError(f"Task with {task_id} couldn't be found")
            # Update the task status
            await cursor.execute("UPDATE tasks SET status = %s WHERE id = %s", (status, task_id))
            # Commit the transaction
            await cursor.execute("COMMIT")
            print(f"Task {task_id} status updated to {status}")

        except NotFoundError as e:
            raise

        except ValueError:
            raise TaskOperationException("Invalid Task ID format.", "400 Bad Request")

        except Exception as e:
            # Rollback in case of error
            await cursor.execute("ROLLBACK")
            print(f"Error occurred: {e}. Task status update rolled back.")