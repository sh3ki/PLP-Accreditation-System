"""
Intelligent caching layer for Firestore operations
Dramatically reduces quota usage while maintaining data freshness
"""
import time
from typing import Any, Dict, List, Optional, Callable
from functools import wraps
import threading

# =============================================================================
# CONFIGURATION
# =============================================================================
# Cache TTLs (in seconds)
CACHE_TTL = {
    'departments': 300,      # 5 minutes - semi-static organizational data
    'programs': 300,         # 5 minutes
    'accreditation_types': 600,  # 10 minutes - very static
    'areas': 600,            # 10 minutes
    'checklists': 180,       # 3 minutes - more dynamic
    'documents': 60,         # 1 minute - frequently updated
    'users': 120,            # 2 minutes - session data
    'roles': 600,            # 10 minutes - very static
    'system_settings': 300,  # 5 minutes
    'reports_history': 60,   # 1 minute
}

DEFAULT_TTL = 60  # 1 minute for uncategorized collections

# =============================================================================
# APPLICATION-LEVEL CACHE (Thread-safe)
# =============================================================================
class FirestoreCache:
    """Thread-safe application-level cache for Firestore data"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
    
    def get(self, collection: str, doc_id: Optional[str] = None) -> Optional[Any]:
        """Get cached data"""
        with self._lock:
            cache_entry = self._cache.get(collection)
            if not cache_entry:
                return None
            
            # Check if expired
            if time.time() > cache_entry['expires_at']:
                del self._cache[collection]
                return None
            
            # Return specific document or all documents
            if doc_id:
                # Handle case where data is a list instead of dict
                data = cache_entry['data']
                if isinstance(data, list):
                    # Search for the document in the list
                    for item in data:
                        if isinstance(item, dict) and item.get('id') == doc_id:
                            return item
                    return None
                elif isinstance(data, dict):
                    return data.get(doc_id)
                return None
            return cache_entry['data']
    
    def set(self, collection: str, data: Any, ttl: Optional[int] = None):
        """Cache data with TTL"""
        if ttl is None:
            ttl = CACHE_TTL.get(collection, DEFAULT_TTL)
        
        with self._lock:
            self._cache[collection] = {
                'data': data,
                'expires_at': time.time() + ttl,
                'cached_at': time.time()
            }
    
    def invalidate(self, collection: str):
        """Invalidate cached collection"""
        with self._lock:
            if collection in self._cache:
                del self._cache[collection]
    
    def clear(self):
        """Clear entire cache"""
        with self._lock:
            self._cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            stats = {
                'collections_cached': len(self._cache),
                'total_size_bytes': 0,
                'entries': []
            }
            
            for collection, entry in self._cache.items():
                age = time.time() - entry['cached_at']
                ttl_remaining = entry['expires_at'] - time.time()
                
                stats['entries'].append({
                    'collection': collection,
                    'age_seconds': round(age, 2),
                    'ttl_remaining': round(ttl_remaining, 2),
                    'is_expired': ttl_remaining <= 0
                })
            
            return stats


# Global cache instance
_firestore_cache = FirestoreCache()


# =============================================================================
# REQUEST-LEVEL CACHE (attached to Django request object)
# =============================================================================
def get_request_cache(request) -> Dict[str, Any]:
    """Get or create request-level cache"""
    if not hasattr(request, '_firestore_cache'):
        request._firestore_cache = {}
    return request._firestore_cache


def cache_key(collection: str, doc_id: Optional[str] = None, **kwargs) -> str:
    """Generate cache key"""
    if doc_id:
        return f"{collection}:{doc_id}"
    
    # For queries, include filter params
    if kwargs:
        params = ':'.join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return f"{collection}:query:{params}"
    
    return f"{collection}:all"


# =============================================================================
# CACHING DECORATORS
# =============================================================================
def cached_firestore_call(ttl: Optional[int] = None):
    """
    Decorator for caching Firestore calls
    Uses both request-level and application-level caching
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Try to extract collection name from args
            collection = args[0] if args else kwargs.get('collection')
            if not collection:
                # Can't cache without collection name
                return func(*args, **kwargs)
            
            # Check if we have request context (from middleware)
            request = kwargs.get('request')
            
            # Generate cache key
            doc_id = args[1] if len(args) > 1 else kwargs.get('doc_id')
            key = cache_key(collection, doc_id, **{k: v for k, v in kwargs.items() if k not in ['request', 'collection', 'doc_id']})
            
            # Try request-level cache first (if available)
            if request:
                req_cache = get_request_cache(request)
                if key in req_cache:
                    return req_cache[key]
            
            # Try application-level cache
            if doc_id:
                # For single document get
                app_cached = _firestore_cache.get(collection, doc_id)
                if app_cached is not None:
                    if request:
                        req_cache[key] = app_cached
                    return app_cached
            else:
                # For get_all
                app_cached = _firestore_cache.get(collection)
                if app_cached is not None:
                    if request:
                        req_cache[key] = app_cached
                    return app_cached
            
            # Cache miss - fetch from Firestore
            result = func(*args, **kwargs)
            
            # Cache the result
            if doc_id:
                # For single document, cache both the document and update collection cache
                all_docs = _firestore_cache.get(collection) or {}
                if isinstance(all_docs, dict) and result:
                    all_docs[doc_id] = result
                    _firestore_cache.set(collection, all_docs, ttl)
            else:
                # For get_all, cache the entire collection
                if isinstance(result, list):
                    # Convert list to dict for easier single-doc lookups
                    docs_dict = {doc.get('id', idx): doc for idx, doc in enumerate(result)}
                    _firestore_cache.set(collection, result, ttl)
            
            # Also cache in request cache
            if request:
                req_cache[key] = result
            
            return result
        
        return wrapper
    return decorator


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def invalidate_collection_cache(collection: str):
    """Invalidate cache for a collection after writes"""
    _firestore_cache.invalidate(collection)


def clear_all_caches():
    """Clear all application-level caches"""
    _firestore_cache.clear()


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    return _firestore_cache.get_stats()


def warmup_cache():
    """Pre-populate cache with frequently accessed static data"""
    from .firebase_utils import get_all_documents
    
    static_collections = [
        'departments',
        'accreditation_types',
        'areas',
        'roles',
        'system_settings',
    ]
    
    for collection in static_collections:
        try:
            data = get_all_documents(collection)
            _firestore_cache.set(collection, data)
        except Exception:
            pass  # Silent fail on warmup


# =============================================================================
# BATCH OPERATIONS HELPER
# =============================================================================
class BatchedFirestoreOps:
    """
    Helper to batch multiple Firestore operations
    Reduces quota by combining reads/writes
    """
    
    def __init__(self):
        self.reads = []
        self.writes = []
        self.updates = []
        self.deletes = []
    
    def queue_read(self, collection: str, doc_id: str):
        """Queue a document read"""
        self.reads.append((collection, doc_id))
    
    def queue_write(self, collection: str, doc_id: str, data: dict):
        """Queue a document write"""
        self.writes.append((collection, doc_id, data))
    
    def queue_update(self, collection: str, doc_id: str, data: dict):
        """Queue a document update"""
        self.updates.append((collection, doc_id, data))
    
    def queue_delete(self, collection: str, doc_id: str):
        """Queue a document delete"""
        self.deletes.append((collection, doc_id))
    
    def execute(self):
        """Execute all batched operations"""
        from .firebase_utils import (
            get_document, create_document, 
            update_document, delete_document
        )
        
        results = {
            'reads': [],
            'writes': [],
            'updates': [],
            'deletes': [],
            'errors': []
        }
        
        # Execute reads
        for collection, doc_id in self.reads:
            try:
                doc = get_document(collection, doc_id)
                results['reads'].append((collection, doc_id, doc))
            except Exception as e:
                results['errors'].append(('read', collection, doc_id, str(e)))
        
        # Execute writes
        for collection, doc_id, data in self.writes:
            try:
                new_id = create_document(collection, data, doc_id)
                results['writes'].append((collection, new_id))
                invalidate_collection_cache(collection)
            except Exception as e:
                results['errors'].append(('write', collection, doc_id, str(e)))
        
        # Execute updates
        for collection, doc_id, data in self.updates:
            try:
                success = update_document(collection, doc_id, data)
                results['updates'].append((collection, doc_id, success))
                invalidate_collection_cache(collection)
            except Exception as e:
                results['errors'].append(('update', collection, doc_id, str(e)))
        
        # Execute deletes
        for collection, doc_id in self.deletes:
            try:
                success = delete_document(collection, doc_id)
                results['deletes'].append((collection, doc_id, success))
                invalidate_collection_cache(collection)
            except Exception as e:
                results['errors'].append(('delete', collection, doc_id, str(e)))
        
        return results
