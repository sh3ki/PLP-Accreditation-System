"""
Example Django views showing how to use Firebase Firestore

This file demonstrates how to integrate Firestore operations in Django views.
"""

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from accreditation.firebase_utils import firestore_helper
import json


def firestore_status(request):
    """
    Check Firestore connection status
    
    GET /firestore/status/
    """
    if firestore_helper.is_connected():
        return JsonResponse({
            'status': 'connected',
            'message': 'Firestore is connected and ready to use'
        })
    else:
        return JsonResponse({
            'status': 'disconnected',
            'message': 'Firestore is not connected'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_document_view(request):
    """
    Create a new document in Firestore
    
    POST /firestore/create/
    Body: {
        "collection": "collection_name",
        "data": { ... document data ... },
        "document_id": "optional_custom_id"
    }
    """
    try:
        body = json.loads(request.body)
        collection_name = body.get('collection')
        document_data = body.get('data')
        document_id = body.get('document_id')
        
        if not collection_name or not document_data:
            return JsonResponse({
                'error': 'Both collection and data are required'
            }, status=400)
        
        doc_id = firestore_helper.create_document(
            collection_name, 
            document_data, 
            document_id
        )
        
        return JsonResponse({
            'success': True,
            'document_id': doc_id,
            'message': 'Document created successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_document_view(request, collection_name, document_id):
    """
    Get a document from Firestore
    
    GET /firestore/get/<collection_name>/<document_id>/
    """
    try:
        document = firestore_helper.get_document(collection_name, document_id)
        
        if document:
            return JsonResponse({
                'success': True,
                'document': document
            })
        else:
            return JsonResponse({
                'error': 'Document not found'
            }, status=404)
            
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_collection_view(request, collection_name):
    """
    Get all documents from a collection
    
    GET /firestore/collection/<collection_name>/
    Optional query parameters:
    - limit: number of documents to return
    """
    try:
        limit = request.GET.get('limit')
        limit = int(limit) if limit else None
        
        documents = firestore_helper.get_all_documents(collection_name, limit)
        
        return JsonResponse({
            'success': True,
            'documents': documents,
            'count': len(documents)
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def update_document_view(request, collection_name, document_id):
    """
    Update a document in Firestore
    
    PUT /firestore/update/<collection_name>/<document_id>/
    Body: { ... data to update ... }
    """
    try:
        body = json.loads(request.body)
        
        success = firestore_helper.update_document(
            collection_name, 
            document_id, 
            body
        )
        
        if success:
            return JsonResponse({
                'success': True,
                'message': 'Document updated successfully'
            })
        else:
            return JsonResponse({
                'error': 'Failed to update document'
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_document_view(request, collection_name, document_id):
    """
    Delete a document from Firestore
    
    DELETE /firestore/delete/<collection_name>/<document_id>/
    """
    try:
        success = firestore_helper.delete_document(collection_name, document_id)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': 'Document deleted successfully'
            })
        else:
            return JsonResponse({
                'error': 'Failed to delete document'
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def query_documents_view(request, collection_name):
    """
    Query documents in a collection
    
    GET /firestore/query/<collection_name>/
    Query parameters:
    - field: field to query on
    - operator: query operator (==, !=, <, <=, >, >=, in, not-in, array-contains)
    - value: value to compare against
    - limit: optional limit on results
    """
    try:
        field = request.GET.get('field')
        operator = request.GET.get('operator')
        value = request.GET.get('value')
        limit = request.GET.get('limit')
        
        if not all([field, operator, value]):
            return JsonResponse({
                'error': 'field, operator, and value are required query parameters'
            }, status=400)
        
        # Convert value to appropriate type
        if value.isdigit():
            value = int(value)
        elif value.lower() in ['true', 'false']:
            value = value.lower() == 'true'
        
        limit = int(limit) if limit else None
        
        documents = firestore_helper.query_documents(
            collection_name, 
            field, 
            operator, 
            value, 
            limit
        )
        
        return JsonResponse({
            'success': True,
            'documents': documents,
            'count': len(documents)
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)