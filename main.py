import asyncio
from Task_Mgmt_System.manager.user_manage import create_user
from Task_Mgmt_System.manager.task_manage import (
    create_task,
    list_tasks,
    get_task,
    update_task,
    delete_task,
    change_task_status
)

async def main():
    print("Welcome to the Task Management System!")

    while True:
        print("\nChoose an option:")
        print("1. Create User")
        print("2. Create Task")
        print("3. List All Tasks")
        print("4. Get a Task")
        print("5. Update Task")
        print("6. Delete Task")
        print("7. Change Task Status")
        print("8. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            username = input("Enter username: ")
            await create_user(username)

        elif choice == "2":
            user_id = int(input("Enter user ID: ")) 
            task_name = input("Enter task name: ")
            task_description = input("Enter task description: ")  
            await create_task(user_id, task_name, task_description) 

        elif choice == "3":
            user_id = int(input("Enter user ID to list tasks: "))  
            tasks = await list_tasks(user_id)
            for task in tasks:
                print(f"Task ID: {task['id']}, Name: {task['name']}, Description: {task['description']}, Status: {task['status']}")
        
        elif choice == "4":
            task_id = input("Enter task ID to get details: ")
            task = await get_task(task_id)
            print(f"Task ID: {task['id']}, Name: {task['name']}, Description: {task['description']}, Status: {task['status']}")
        
        elif choice == "5":
            task_id = input("Enter task ID to update: ")
            new_name = input("Enter new task name: ")
            new_description = input("Enter new task description: ")  
            await update_task(task_id, new_name, new_description)  
        
        elif choice == "6":
            task_id = input("Enter task ID to delete: ")
            await delete_task(task_id)
        
        elif choice == "7":
            task_id = input("Enter task ID to change status: ")
            status = input("Enter new status (Active/Archive): ")
            await change_task_status(task_id, status)
        
        elif choice == "8":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    asyncio.run(main())
