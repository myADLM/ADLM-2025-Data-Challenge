"""
URL configuration for chat_web_dj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from api.views import (
    api,
    document_view,
    document_list_view,
    pdf_page_image_view,
    pdf_page_view,
    chunk_lengths_histogram,
    marker_chunks_view,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("documents/", document_list_view, name="document_list"),
    path("documents/<int:document_id>/", document_view, name="document_view"),
    path(
        "documents/<int:document_id>/page/<int:page_index>.jpg",
        pdf_page_image_view,
        name="pdf_page_image",
    ),
    path(
        "documents/<int:document_id>/marker",
        marker_chunks_view,
        name="marker_chunks_view",
    ),
    path(
        "pdf/<int:document_id>/<int:page_number>/",
        pdf_page_view,
        name="pdf_page_view",
    ),
    path(
        "stats/chunk_lengths.png",
        chunk_lengths_histogram,
        name="chunk_lengths_histogram",
    ),
    path("", document_list_view),  # Redirect root to document list
]
