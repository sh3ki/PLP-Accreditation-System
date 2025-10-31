"""
Middleware to attach request-level caching and provide cache statistics
"""
from django.utils.deprecation import MiddlewareMixin
from .cache_utils import get_request_cache, get_cache_stats
import logging

logger = logging.getLogger(__name__)


class FirestoreCacheMiddleware(MiddlewareMixin):
    """
    Middleware to enable request-level Firestore caching
    Also logs cache hit rates for monitoring
    """
    
    def process_request(self, request):
        """Initialize request cache"""
        # Cache will be auto-created by get_request_cache on first access
        # Just ensure request object is ready
        request._cache_hits = 0
        request._cache_misses = 0
        return None
    
    def process_response(self, request, response):
        """Log cache statistics for this request"""
        if hasattr(request, '_firestore_cache'):
            cache_size = len(request._firestore_cache)
            hits = getattr(request, '_cache_hits', 0)
            misses = getattr(request, '_cache_misses', 0)
            
            # Only log if there was cache activity
            if cache_size > 0 or hits > 0 or misses > 0:
                hit_rate = (hits / (hits + misses) * 100) if (hits + misses) > 0 else 0
                logger.debug(
                    f"Firestore Cache - Request: {request.path} | "
                    f"Items: {cache_size} | Hits: {hits} | Misses: {misses} | "
                    f"Hit Rate: {hit_rate:.1f}%"
                )
        
        return response
