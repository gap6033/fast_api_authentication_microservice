import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Set up a basic logger
logger = logging.getLogger("myapp.middleware")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_body = await request.body()

        # Log incoming request
        logger.info(f"Incoming request: {request.method} {request.url.path}")
        logger.debug(f"Headers: {dict(request.headers)}")
        if request_body:
            logger.debug(f"Body: {request_body.decode('utf-8')}")

        try:
            response: Response = await call_next(request)
        except Exception as exc:
            logger.exception("Request processing failed")
            raise

        process_time = (time.time() - start_time) * 1000
        logger.info(f"Response status: {response.status_code} - Time taken: {process_time:.2f} ms")

        return response
