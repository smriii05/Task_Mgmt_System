class DatabaseException(Exception):
    def __init__(self, message="Database error occurred", status = "500 Internal Server Error"):
        self.message = message
        self.status = status
        super().__init__(self.message)

class UserCreationException(DatabaseException):
    def __init__(self, message="User creation failed", status = "400 Bad Request"):
        super().__init__(message, status)

class TaskOperationException(DatabaseException):
    def __init__(self, message="Couldn't Perform Task operation.", status = "500 Internal Server Error"):
        super().__init__(message, status)

class NotFoundError(DatabaseException):
    def __init__(self, message="Resource not found.", status="404 Not Found"):
        super().__init__(message, status)

class BadRequestError(DatabaseException):
    def __init__(self, message="Bad request. Please enter valid information.", status ="400 Bad Request"):
        super().__init__(message, status)

class InternalServerError(DatabaseException):
    def __init__(self, message="An unexpected error occured.", status ="500 Internal Server Error"):
        super().__init__(message, status)

class ErrorResponse:
    @staticmethod
    def create_error_response(message, error_status):
        return {"error": message, "status": error_status}
