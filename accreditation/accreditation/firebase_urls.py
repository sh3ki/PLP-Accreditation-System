"""
URL patterns for Firebase Firestore API endpoints
"""

from django.urls import path
from . import firebase_views

urlpatterns = [
    # Status endpoint
    path('status/', firebase_views.firestore_status, name='firestore_status'),
    
    # CRUD operations
    path('create/', firebase_views.create_document_view, name='create_document'),
    path('get/<str:collection_name>/<str:document_id>/', firebase_views.get_document_view, name='get_document'),
    path('collection/<str:collection_name>/', firebase_views.get_collection_view, name='get_collection'),
    path('update/<str:collection_name>/<str:document_id>/', firebase_views.update_document_view, name='update_document'),
    path('delete/<str:collection_name>/<str:document_id>/', firebase_views.delete_document_view, name='delete_document'),
    
    # Query endpoint
    path('query/<str:collection_name>/', firebase_views.query_documents_view, name='query_documents'),
]