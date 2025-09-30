# Django Firebase Firestore Integration

This Django project is configured to use Firebase Firestore as the database. Follow the setup instructions below to get started.

## Project Information
- **Project Name**: accreditation
- **Project ID**: accreditation-6af94
- **Project Number**: 662108211681

## Setup Instructions

### 1. Install Dependencies
The required packages are already installed:
- `firebase-admin` - Firebase Admin SDK
- `google-cloud-firestore` - Firestore client library

### 2. Firebase Service Account Setup

**IMPORTANT**: You need to download the service account key from Firebase Console.

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your **"accreditation"** project
3. Click the gear icon ⚙️ next to "Project Overview"
4. Select **"Project settings"**
5. Click on the **"Service accounts"** tab
6. Click **"Generate new private key"**
7. Click **"Generate key"** to download the JSON file
8. Save the file as `firebase-service-account.json` in the project root directory
9. **Never commit this file to version control!** (It's already in .gitignore)

### 3. Enable Firestore Database

Make sure Firestore is enabled in your Firebase project:

1. In Firebase Console, go to **"Firestore Database"**
2. Click **"Create database"**
3. Choose **"Start in test mode"** (you can change security rules later)
4. Select a location for your database

### 4. Test the Connection

Run the test command to verify everything is working:

```bash
python manage.py test_firebase
```

This command will:
- ✅ Test Firebase connection
- ✅ Test document creation
- ✅ Test document reading
- ✅ Test document updating
- ✅ Test document querying
- ✅ Test document deletion

## Usage Examples

### Using Firebase Helper Functions

```python
from accreditation.firebase_utils import firestore_helper

# Create a document
data = {'name': 'John Doe', 'email': 'john@example.com'}
doc_id = firestore_helper.create_document('users', data)

# Get a document
user = firestore_helper.get_document('users', doc_id)

# Update a document
firestore_helper.update_document('users', doc_id, {'status': 'active'})

# Query documents
active_users = firestore_helper.query_documents('users', 'status', '==', 'active')

# Delete a document
firestore_helper.delete_document('users', doc_id)
```

### Using Convenience Functions

```python
from accreditation.firebase_utils import create_document, get_document, update_document

# Shorter syntax
doc_id = create_document('users', {'name': 'Jane Doe'})
user = get_document('users', doc_id)
update_document('users', doc_id, {'last_login': datetime.now()})
```

### Using REST API Endpoints

The project includes REST API endpoints for Firestore operations:

- `GET /firestore/status/` - Check connection status
- `POST /firestore/create/` - Create a document
- `GET /firestore/get/<collection>/<document_id>/` - Get a document
- `GET /firestore/collection/<collection>/` - Get all documents from a collection
- `PUT /firestore/update/<collection>/<document_id>/` - Update a document
- `DELETE /firestore/delete/<collection>/<document_id>/` - Delete a document
- `GET /firestore/query/<collection>/` - Query documents

#### Example API Usage

```bash
# Check status
curl http://localhost:8000/firestore/status/

# Create a document
curl -X POST http://localhost:8000/firestore/create/ \
  -H "Content-Type: application/json" \
  -d '{"collection": "users", "data": {"name": "John Doe", "email": "john@example.com"}}'

# Get a document
curl http://localhost:8000/firestore/get/users/document_id/

# Query documents
curl "http://localhost:8000/firestore/query/users/?field=status&operator==&value=active"
```

## File Structure

```
accreditation/
├── firebase-service-account.json      # Service account key (you need to add this)
├── accreditation/
│   ├── settings.py                    # Firebase configuration
│   ├── firebase_utils.py              # Firebase helper functions
│   ├── firebase_views.py              # REST API views
│   ├── firebase_urls.py               # URL patterns for Firebase API
│   └── management/
│       └── commands/
│           └── test_firebase.py       # Test command
└── .gitignore                         # Excludes service account key
```

## Important Notes

### Security
- **Never commit `firebase-service-account.json` to version control**
- The file is already added to `.gitignore`
- In production, use environment variables or secure secret management

### Database Structure
- Firestore is a NoSQL document database
- Data is stored in collections and documents
- Documents can contain subcollections
- All documents automatically get `created_at` and `updated_at` timestamps

### Error Handling
- All operations include proper error handling
- Check `firestore_helper.is_connected()` before operations
- Use try-catch blocks for database operations

## Firestore vs Traditional SQL

| Traditional SQL | Firestore |
|----------------|-----------|
| Tables | Collections |
| Rows | Documents |
| Columns | Fields |
| Foreign Keys | References |
| JOINs | Not available (use subcollections or references) |

## Next Steps

1. **Download the service account key** (most important!)
2. **Run the test command** to verify setup
3. **Start building your Django models** using Firestore
4. **Create your application logic** using the provided helper functions
5. **Set up proper security rules** in Firebase Console

## Need Help?

If you encounter any issues:

1. Make sure the service account file exists and is named correctly
2. Check that Firestore is enabled in your Firebase project
3. Verify your Firebase project ID matches the configuration
4. Run the test command to diagnose connection issues

## Firebase Console Links

- [Firebase Console](https://console.firebase.google.com/)
- [Your Project](https://console.firebase.google.com/project/accreditation-6af94)
- [Firestore Database](https://console.firebase.google.com/project/accreditation-6af94/firestore)
- [Project Settings](https://console.firebase.google.com/project/accreditation-6af94/settings/general)