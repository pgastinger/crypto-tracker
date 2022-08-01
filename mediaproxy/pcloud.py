# PCloud storage class for Django pluggable storage system, based on Dropbox version
# Author: Anthony Monthe <anthony.monthe@gmail.com>
# License: BSD
#
# Usage:
#
# Add below to settings.py:
#  PCLOUD_OAUTH2_TOKEN = 'token'
#  DEFAULT_FILE_STORAGE = 'mediaproxy.pcloud.PCloudStorage'

from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import File
from django.core.files.storage import Storage
from django.utils._os import safe_join
from django.utils.deconstruct import deconstructible

from pcloud import PyCloud
from django.conf import settings


class PCloudFile(File):
    def __init__(self, name, storage):
        self.name = name
        self._storage = storage

        (
            self.file_metadata,
            self.file_content,
        ) = self._storage._get_file_content_with_metadata(self.name)


@deconstructible
class PCloudStorage(Storage):
    """DropBox Storage class for Django pluggable storage system."""

    oauth2_access_token = settings.PCLOUD_OAUTH2_TOKEN
    endpoint = "eapi"
    root_path = "/"

    CHUNK_SIZE = 4 * 1024 * 1024

    def __init__(self, oauth2_access_token=oauth2_access_token):
        if oauth2_access_token is None:
            raise ImproperlyConfigured(
                "You must configure an auth token at" "'settings.PCLOUD_OAUTH2_TOKEN'."
            )
        self.client = PyCloud(
            username="",
            password=self.oauth2_access_token,
            endpoint=self.endpoint,
            oauth2=True,
        )

    def _full_path(self, name):
        if name == "/":
            name = ""
        return safe_join(self.root_path, name).replace("\\", "/")

    def _get_file_metadata(self, filename):
        folder_details = self.client.listfolder(folderid=0)
        for file in folder_details["metadata"]["contents"]:
            fname = file["path"]
            if fname == filename:
                return file
        return {}

    def _get_file_content_with_metadata(self, filename):
        print(filename)
        md = self._get_file_metadata(self._full_path(filename))
        assert bool(md), f"File {filename} not found"
        fd = self.client.file_open(flags="", fileid=md["fileid"])
        fs = self.client.file_size(fd=fd["fd"])
        return md, self.client.file_read(fd=fd["fd"], count=fs["size"])

    def delete(self, filename):
        md = self._get_file_metadata(self._full_path(filename))
        assert bool(md), "File not found"
        self.client.deletefile(fileid=md["fileid"])

    def exists(self, filename):
        try:
            return bool(self._get_file_metadata(self._full_path(filename)))
        except Exception as e:
            return False

    def listdir(self):
        directories, files = [], []
        metadata = self.client.listfolder(folderid=0)
        for entry in metadata["metadata"]["contents"]:
            if entry["isfolder"]:
                directories.append(entry["name"])
            else:
                files.append(entry["name"])
        return directories, files

    def size(self, filename):
        metadata = self._get_file_metadata(self._full_path(filename))
        return metadata["size"]

    def modified_time(self, filename):
        metadata = self._get_file_metadata(self._full_path(filename))
        return metadata["modified"]

    def created_time(self, filename):
        metadata = self._get_file_metadata(self._full_path(filename))
        return metadata["created"]

    def _get_link_for_file(self, filename):
        md = self._get_file_metadata(self._full_path(filename))
        assert bool(md), "File not found"
        download_link = self.client._do_request("getfilepublink", fileid=md["fileid"])
        download_details = self.client._do_request(
            "getpublinkdownload", code=download_link["code"]
        )
        return f'https://{download_details["hosts"][0]}{download_details["path"]}'

    def url(self, filename):
        return f"/media/{filename}"

    def _open(self, filename, mode="rb"):
        remote_file = PCloudFile(self._full_path(filename), self)
        return remote_file

    def _save(self, name, content):
        content.open()
        self.client.uploadfile(data=content.read(), filename=name, folderid="0")
        content.close()
        return name.replace("/", "")

