from django.urls import path
from .views import upload_documents, upload_test_view  # ✅ Removed upload_form
from .query_with_retrieval import query_with_retrieval  

urlpatterns = [
    path('upload-documents/', upload_documents, name='upload_documents'),
    path('query/', query_with_retrieval, name='query_with_retrieval'),
    path('upload-test/', upload_test_view, name='upload_test'),
]
