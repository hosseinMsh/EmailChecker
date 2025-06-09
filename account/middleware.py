import logging
import time
from django.utils import timezone

logger = logging.getLogger('security')


class LoggingMiddleware:
    """Middleware to log all requests and responses"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before the view is called
        start_time = time.time()

        # Log the request
        logger.info(
            f"Request: {request.method} {request.path} from {request.META.get('REMOTE_ADDR')} "
            f"user: {request.user if request.user.is_authenticated else 'Anonymous'}"
        )

        response = self.get_response(request)

        # Code to be executed for each request/response after the view is called
        duration = time.time() - start_time

        # Log the response
        logger.info(
            f"Response: {request.method} {request.path} completed in {duration:.2f}s "
            f"with status {response.status_code}"
        )

        return response
