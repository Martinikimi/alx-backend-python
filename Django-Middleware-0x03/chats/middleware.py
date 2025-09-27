
import logging
from datetime import datetime

# Configure logger for request logging
logger = logging.getLogger(__name__)
handler = logging.FileHandler("requests.log")   # Logs saved to requests.log
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get user info
        user = request.user if request.user.is_authenticated else "Anonymous"

        # Log timestamp, user, and request path
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)

        # Continue request-response cycle
        response = self.get_response(request)
        return response
