"""
Firebase Firestore Database Helper for Django

This module provides utility functions to interact with Firestore database.
It includes common CRUD operations and helper methods for Django integration.
"""

from firebase_admin import firestore
from django.conf import settings
from datetime import datetime
from typing import Dict, List, Optional, Any
import json


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
            doc_ref.update(update_data)
            return True
        except Exception as e:
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


# Convenience functions
def create_document(collection_name: str, document_data: Dict[str, Any], document_id: Optional[str] = None) -> str:
    """Create a document in Firestore"""
    return firestore_helper.create_document(collection_name, document_data, document_id)


def get_document(collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
    """Get a document from Firestore"""
    return firestore_helper.get_document(collection_name, document_id)


def get_all_documents(collection_name: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get all documents from a collection"""
    return firestore_helper.get_all_documents(collection_name, limit)


def query_documents(collection_name: str, field: str, operator: str, value: Any, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Query documents in a collection"""
    return firestore_helper.query_documents(collection_name, field, operator, value, limit)


def update_document(collection_name: str, document_id: str, update_data: Dict[str, Any]) -> bool:
    """Update a document in Firestore"""
    return firestore_helper.update_document(collection_name, document_id, update_data)


def delete_document(collection_name: str, document_id: str) -> bool:
    """Delete a document from Firestore"""
    return firestore_helper.delete_document(collection_name, document_id)