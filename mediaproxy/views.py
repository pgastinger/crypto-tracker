from django.shortcuts import render
from .pcloud import PCloudStorage
from django.http import HttpResponse
from pprint import pprint


def index(request, filename):
    pcs = PCloudStorage()
    f = pcs._open(filename)
    response = HttpResponse(content_type=f.file_metadata["contenttype"])
    response.write(f.file_content)
    return response
