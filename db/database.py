import aiomysql
import asyncio
from contextlib import asynccontextmanager
from exception_handler import DatabaseException, ErrorResponse

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
    except ConnectionError as ce:
        print(f"Couldn't connect to the database, {ce}")
    finally:
        conn.close()

async def init_db():
    """
    Initializes the database by creating the `users` and `tasks` tables 
    if they do not already exist.
    """
    try:
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
    
    except DatabaseException as e:
        error_response = ErrorResponse.create_error_response(str(e), e.status)
        print(error_response)
        return None
    
    except Exception as e:
        if "already exists" in str(e).lower():
            raise DatabaseException("Table Already Exists.", "409 Conflict")


if __name__ == "__main__":
    asyncio.run(init_db())
