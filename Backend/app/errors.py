class AppError(Exception):
    def __init__(self, message: str, status: int = 400, code: str = "invalid_request"):
        super().__init__(message)
        self.message, self.status, self.code = message, status, code


class StaleLease(AppError):
    def __init__(self):
        super().__init__("This analysis no longer owns the conversation. Start a new turn.", 409, "stale_run")
