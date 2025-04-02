"""
User-related operations such as creating a user.
"""
from db.database import get_db

async def create_user(username: str):
    async with get_db() as cursor:
        await cursor.execute("INSERT INTO users (username) VALUES (%s)", (username,))
        await cursor.execute("SELECT LAST_INSERT_ID()")  
        user_id = await cursor.fetchone()
    
    user_id = user_id["LAST_INSERT_ID()"]
    print(f"User {username} created successfully with ID {user_id}")
    return user_id 
