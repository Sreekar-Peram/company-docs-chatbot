from django.urls import path
from .views import upload_documents, query_llama

urlpatterns = [
    path('upload-documents/', upload_documents, name='upload_documents'),
    path('query/', query_llama, name='query_llama'),
]
