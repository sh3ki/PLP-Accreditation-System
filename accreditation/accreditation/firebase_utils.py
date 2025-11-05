"""
Firebase Firestore Database Helper for Django

This area provides utility functions to interact with Firestore database.
It includes common CRUD operations and helper methods for Django integration.
"""

from firebase_admin import firestore
from django.conf import settings
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import time
from google.api_core.exceptions import ResourceExhausted, DeadlineExceeded
from functools import wraps


def retry_on_quota_exceeded(max_retries=3, initial_delay=1):
    """
    Decorator to retry Firestore operations when quota is exceeded
    Uses exponential backoff
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except ResourceExhausted as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        print(f"Quota exceeded, retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                        delay *= 2  # Exponential backoff
                    else:
                        # On final attempt, raise a more user-friendly error
                        raise Exception("Firebase quota exceeded. Please try again in a few moments or contact support.")
                except DeadlineExceeded as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        print(f"Request timeout, retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                        delay *= 2
                    else:
                        raise Exception("Request timeout. Please try again.")
                except Exception as e:
                    # For other exceptions, don't retry
                    raise e
            
            # If we got here, all retries failed
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


class FirestoreHelper:
    """
    Helper class for Firestore database operations
    """
    
    def __init__(self):
        """Initialize Firestore client"""
        try:
            self.db = firestore.client()
        except Exception as e:
            print(f"Error initializing Firestore client: {e}")
            self.db = None
    
    def is_connected(self) -> bool:
        """Check if Firestore is properly connected"""
        return self.db is not None
    
    # CREATE operations
    def create_document(self, collection_name: str, document_data: Dict[str, Any], document_id: Optional[str] = None) -> str:
        """
        Create a new document in Firestore
        
        Args:
            collection_name: Name of the collection
            document_data: Data to store in the document
            document_id: Optional custom document ID
        
        Returns:
            str: Document ID of created document
        """
        if not self.is_connected():
            raise Exception("Firestore not connected")
        
        # Add timestamp
        document_data['created_at'] = datetime.now()
        document_data['updated_at'] = datetime.now()
        
        try:
            if document_id:
                # Create with custom ID
                doc_ref = self.db.collection(collection_name).document(document_id)
                doc_ref.set(document_data)
                return document_id
            else:
                # Auto-generate ID
                doc_ref = self.db.collection(collection_name).add(document_data)
                return doc_ref[1].id
        except Exception as e:
            raise Exception(f"Error creating document: {e}")
    
    # READ operations
    @retry_on_quota_exceeded(max_retries=3, initial_delay=1)
    def get_document(self, collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single document from Firestore
        
        Args:
            collection_name: Name of the collection
            document_id: ID of the document
        
        Returns:
            Dict containing document data or None if not found
        """
        if not self.is_connected():
            raise Exception("Firestore not connected")
        
        try:
            doc_ref = self.db.collection(collection_name).document(document_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id  # Add document ID to the data
                return data
            return None
        except Exception as e:
            raise Exception(f"Error getting document: {e}")
    
    @retry_on_quota_exceeded(max_retries=3, initial_delay=1)
    def get_all_documents(self, collection_name: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all documents from a collection
        
        Args:
            collection_name: Name of the collection
            limit: Optional limit on number of documents
        
        Returns:
            List of dictionaries containing document data
        """
        if not self.is_connected():
            raise Exception("Firestore not connected")
        
        try:
            query = self.db.collection(collection_name)
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            documents = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                documents.append(data)
            
            return documents
        except Exception as e:
            raise Exception(f"Error getting documents: {e}")
    
    @retry_on_quota_exceeded(max_retries=3, initial_delay=1)
    def query_documents(self, collection_name: str, field: str, operator: str, value: Any, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Query documents based on field conditions
        
        Args:
            collection_name: Name of the collection
            field: Field name to query
            operator: Query operator ('==', '!=', '<', '<=', '>', '>=', 'in', 'not-in', 'array-contains')
            value: Value to compare against
            limit: Optional limit on results
        
        Returns:
            List of matching documents
        """
        if not self.is_connected():
            raise Exception("Firestore not connected")
        
        try:
            query = self.db.collection(collection_name).where(field, operator, value)
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            documents = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                documents.append(data)
            
            return documents
        except Exception as e:
            raise Exception(f"Error querying documents: {e}")
    
    # UPDATE operations
    def update_document(self, collection_name: str, document_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update an existing document
        
        Args:
            collection_name: Name of the collection
            document_id: ID of the document to update
            update_data: Data to update
        
        Returns:
            bool: True if successful
        """
        if not self.is_connected():
            raise Exception("Firestore not connected")
        
        try:
            # Add updated timestamp
            update_data['updated_at'] = datetime.now()
            
            doc_ref = self.db.collection(collection_name).document(document_id)
            
            # Use set with merge=True to update or create if doesn't exist
            doc_ref.set(update_data, merge=True)
            print(f"Successfully updated document {document_id} in {collection_name}")
            return True
        except Exception as e:
            print(f"Error updating document {document_id} in {collection_name}: {e}")
            raise Exception(f"Error updating document: {e}")
    
    # DELETE operations
    def delete_document(self, collection_name: str, document_id: str) -> bool:
        """
        Delete a document from Firestore
        
        Args:
            collection_name: Name of the collection
            document_id: ID of the document to delete
        
        Returns:
            bool: True if successful
        """
        if not self.is_connected():
            raise Exception("Firestore not connected")
        
        try:
            doc_ref = self.db.collection(collection_name).document(document_id)
            doc_ref.delete()
            return True
        except Exception as e:
            raise Exception(f"Error deleting document: {e}")
    
    def delete_collection(self, collection_name: str, batch_size: int = 100) -> bool:
        """
        Delete all documents in a collection
        
        Args:
            collection_name: Name of the collection
            batch_size: Number of documents to delete in each batch
        
        Returns:
            bool: True if successful
        """
        if not self.is_connected():
            raise Exception("Firestore not connected")
        
        try:
            docs = self.db.collection(collection_name).limit(batch_size).stream()
            deleted = 0
            
            for doc in docs:
                doc.reference.delete()
                deleted += 1
            
            if deleted >= batch_size:
                # Recursively delete remaining documents
                return self.delete_collection(collection_name, batch_size)
            
            return True
        except Exception as e:
            raise Exception(f"Error deleting collection: {e}")
    
    # Utility methods
    def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists and has documents
        
        Args:
            collection_name: Name of the collection
        
        Returns:
            bool: True if collection exists and has documents
        """
        if not self.is_connected():
            return False
        
        try:
            docs = self.db.collection(collection_name).limit(1).stream()
            return len(list(docs)) > 0
        except Exception:
            return False
    
    def get_collection_count(self, collection_name: str) -> int:
        """
        Get the number of documents in a collection
        
        Args:
            collection_name: Name of the collection
        
        Returns:
            int: Number of documents
        """
        if not self.is_connected():
            return 0
        
        try:
            docs = self.db.collection(collection_name).stream()
            return len(list(docs))
        except Exception:
            return 0


# Global instance
firestore_helper = FirestoreHelper()

# Import caching utilities
try:
    from .cache_utils import (
        _firestore_cache,
        invalidate_collection_cache,
        CACHE_TTL,
        DEFAULT_TTL,
    )
    # CACHING DISABLED - Causes stale data issues
    CACHING_ENABLED = False
except ImportError:
    CACHING_ENABLED = False


# Cached convenience functions with quota optimization
def get_document(collection_name: str, document_id: str, request=None) -> Optional[Dict[str, Any]]:
    """
    Get a document from Firestore with intelligent caching
    
    Args:
        collection_name: Name of the collection
        document_id: ID of the document
        request: Optional Django request object for request-level caching
    
    Returns:
        Document data or None
    """
    if not CACHING_ENABLED:
        return firestore_helper.get_document(collection_name, document_id)
    
    # Check request cache first
    if request and hasattr(request, '_firestore_cache'):
        cache_key = f"{collection_name}:{document_id}"
        if cache_key in request._firestore_cache:
            if hasattr(request, '_cache_hits'):
                request._cache_hits += 1
            return request._firestore_cache[cache_key]
    
    # Check application cache
    cached = _firestore_cache.get(collection_name, document_id)
    if cached is not None:
        if request:
            if not hasattr(request, '_firestore_cache'):
                request._firestore_cache = {}
            request._firestore_cache[f"{collection_name}:{document_id}"] = cached
            if hasattr(request, '_cache_hits'):
                request._cache_hits += 1
        return cached
    
    # Cache miss - fetch from Firestore
    if request and hasattr(request, '_cache_misses'):
        request._cache_misses += 1
    
    result = firestore_helper.get_document(collection_name, document_id)
    
    # Cache the result if found
    if result:
        # Update application cache
        all_docs = _firestore_cache.get(collection_name) or {}
        if not isinstance(all_docs, list):
            all_docs = {}
        all_docs[document_id] = result
        ttl = CACHE_TTL.get(collection_name, DEFAULT_TTL)
        _firestore_cache.set(collection_name, all_docs, ttl)
        
        # Update request cache
        if request and hasattr(request, '_firestore_cache'):
            request._firestore_cache[f"{collection_name}:{document_id}"] = result
    
    return result


def get_all_documents(collection_name: str, limit: Optional[int] = None, request=None) -> List[Dict[str, Any]]:
    """
    Get all documents from a collection with intelligent caching
    
    Args:
        collection_name: Name of the collection
        limit: Optional limit on number of documents
        request: Optional Django request object for request-level caching
    
    Returns:
        List of documents
    """
    if not CACHING_ENABLED:
        return firestore_helper.get_all_documents(collection_name, limit)
    
    # Check request cache first
    if request and hasattr(request, '_firestore_cache'):
        cache_key = f"{collection_name}:all:{limit or 'unlimited'}"
        if cache_key in request._firestore_cache:
            if hasattr(request, '_cache_hits'):
                request._cache_hits += 1
            return request._firestore_cache[cache_key]
    
    # Check application cache (only if no limit or full collection is cached)
    if not limit:
        cached = _firestore_cache.get(collection_name)
        if cached is not None and isinstance(cached, list):
            if request:
                if not hasattr(request, '_firestore_cache'):
                    request._firestore_cache = {}
                request._firestore_cache[f"{collection_name}:all:unlimited"] = cached
                if hasattr(request, '_cache_hits'):
                    request._cache_hits += 1
            return cached
    
    # Cache miss - fetch from Firestore
    if request and hasattr(request, '_cache_misses'):
        request._cache_misses += 1
    
    result = firestore_helper.get_all_documents(collection_name, limit)
    
    # Cache the result (only cache full collections without limits)
    if not limit and result:
        ttl = CACHE_TTL.get(collection_name, DEFAULT_TTL)
        _firestore_cache.set(collection_name, result, ttl)
        
        # Update request cache
        if request and hasattr(request, '_firestore_cache'):
            request._firestore_cache[f"{collection_name}:all:unlimited"] = result
    
    return result


def query_documents(collection_name: str, field: str, operator: str, value: Any, limit: Optional[int] = None, request=None) -> List[Dict[str, Any]]:
    """
    Query documents in a collection with caching
    
    Note: Query results are cached at request level only due to dynamic nature
    """
    if not CACHING_ENABLED:
        return firestore_helper.query_documents(collection_name, field, operator, value, limit)
    
    # Check request cache first
    if request and hasattr(request, '_firestore_cache'):
        cache_key = f"{collection_name}:query:{field}:{operator}:{value}:{limit or 'unlimited'}"
        if cache_key in request._firestore_cache:
            if hasattr(request, '_cache_hits'):
                request._cache_hits += 1
            return request._firestore_cache[cache_key]
    
    # Cache miss - execute query
    if request and hasattr(request, '_cache_misses'):
        request._cache_misses += 1
    
    result = firestore_helper.query_documents(collection_name, field, operator, value, limit)
    
    # Cache in request cache only (queries are too dynamic for app-level cache)
    if request:
        if not hasattr(request, '_firestore_cache'):
            request._firestore_cache = {}
        cache_key = f"{collection_name}:query:{field}:{operator}:{value}:{limit or 'unlimited'}"
        request._firestore_cache[cache_key] = result
    
    return result


def create_document(collection_name: str, document_data: Dict[str, Any], document_id: Optional[str] = None) -> str:
    """Create a document in Firestore and invalidate cache"""
    result = firestore_helper.create_document(collection_name, document_data, document_id)
    
    # Invalidate cache for this collection
    if CACHING_ENABLED:
        invalidate_collection_cache(collection_name)
    
    return result


def update_document(collection_name: str, document_id: str, update_data: Dict[str, Any]) -> bool:
    """Update a document in Firestore and invalidate cache"""
    try:
        result = firestore_helper.update_document(collection_name, document_id, update_data)
        
        # Invalidate cache for this collection
        if CACHING_ENABLED:
            invalidate_collection_cache(collection_name)
        
        return result
    except Exception as e:
        print(f"Error in update_document wrapper: {e}")
        import traceback
        traceback.print_exc()
        return False


def delete_document(collection_name: str, document_id: str) -> bool:
    """Delete a document from Firestore and invalidate cache"""
    result = firestore_helper.delete_document(collection_name, document_id)
    
    # Invalidate cache for this collection
    if CACHING_ENABLED:
        invalidate_collection_cache(collection_name)
    
    return result


def upload_profile_image(file, file_path: str) -> str:
    """
    Upload a profile image to Firebase Storage (or local storage for now)
    
    Args:
        file: File object to upload
        file_path: Path where file should be stored
    
    Returns:
        str: URL of uploaded file
    """
    # For now, we'll use a simple approach - store file locally and return a path
    # In production, you'd want to use Firebase Storage or another cloud storage service
    
    import os
    from django.conf import settings
    
    # Create media directory if it doesn't exist
    media_root = os.path.join(settings.BASE_DIR, 'media', 'profile_images')
    os.makedirs(media_root, exist_ok=True)
    
    # Generate unique filename
    import uuid
    file_extension = os.path.splitext(file.name)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_full_path = os.path.join(media_root, unique_filename)
    
    # Save file
    with open(file_full_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    
    # Return relative URL
    return f"/media/profile_images/{unique_filename}"