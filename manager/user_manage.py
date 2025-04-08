"""
User-related operations such as creating a user.
"""
from db.database import get_db
from exception_handler import DatabaseException, BadRequestError, UserCreationException

async def create_user(username: str):
    try:
        async with get_db() as cursor:

            # Check if the username contains only numbers (invalid case)
            if username.isdigit():
                raise BadRequestError(f"Invalid username: '{username}'. Username cannot be numeric.")
            # Check if user already exists
            await cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
            existing_user = await cursor.fetchone()
            
            if existing_user:
                # Raise DuplicateUserException if username is already taken
                raise UserCreationException("User Already Exists.", "409 COnflict")
            
            await cursor.execute("INSERT INTO users (username) VALUES (%s)", (username,))
            await cursor.execute("SELECT LAST_INSERT_ID()")  
            user_id = await cursor.fetchone()

            if not user_id:
                # If there was an issue with inserting the user, raise UserCreationException
                raise UserCreationException("Failed to insert user into the database.")
        
        user_id = user_id["LAST_INSERT_ID()"]
        print(f"User {username} created successfully with ID {user_id}")
        return user_id 
        
    except BadRequestError as e:
        raise

    except UserCreationException as e:
        raise
        
    except DatabaseException as e:
        raise
        
     
