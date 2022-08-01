from django.shortcuts import render
from .pcloud import PCloudStorage
from django.http import HttpResponse


def index(request, filename):
    f = PCloudStorage()._open(filename)
    response = HttpResponse(content_type=f.file_metadata["contenttype"])
    response.write(f.file_content)
    return response
