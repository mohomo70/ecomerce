"""
Custom middleware for the ecommerce project.
"""
import time
import logging
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class DatabaseQueryTimeMiddleware(MiddlewareMixin):
    """
    Middleware to log database query times per request.
    """
    
    def process_request(self, request):
        """Reset query count and time at start of request."""
        request._db_query_count = 0
        request._db_query_time = 0
        request._start_time = time.time()
    
    def process_response(self, request, response):
        """Log database query statistics at end of request."""
        if hasattr(request, '_start_time'):
            total_time = time.time() - request._start_time
            
            # Get database query statistics
            db_query_count = len(connection.queries)
            db_query_time = sum(
                float(query['time']) for query in connection.queries
            )
            
            # Log performance metrics
            logger.info(
                f"Request: {request.method} {request.path} | "
                f"Total time: {total_time:.3f}s | "
                f"DB queries: {db_query_count} | "
                f"DB time: {db_query_time:.3f}s"
            )
            
            # Add performance headers for debugging
            response['X-DB-Query-Count'] = str(db_query_count)
            response['X-DB-Query-Time'] = f"{db_query_time:.3f}s"
            response['X-Total-Time'] = f"{total_time:.3f}s"
        
        return response