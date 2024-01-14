from django.urls import path

from . import views

app_name = "m"

urlpatterns = [
    path('<path:filename>', views.index, name='get-media-file'),
]

