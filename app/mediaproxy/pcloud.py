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
from dataclasses import dataclass

@dataclass
class PCloudEntry:
    name: str
    id: int
    parent_folder_id: int
    raw: dict
    

class PCloudFile(File):
    def __init__(self, name, storage):
        self.name = name
        self._storage = storage

        (
            self.file_metadata,
            self.file_content,
        ) = self._storage._get_file_content_with_metadata(self.name)


class FileNotFoundException(Exception):
    pass

@deconstructible
class PCloudStorage(Storage):
    """DropBox Storage class for Django pluggable storage system."""

    oauth2_access_token = settings.PCLOUD_OAUTH2_TOKEN
    endpoint = "eapi"
    root_path = "/"

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


    def _get_file_content_with_metadata(self, filename):
        md = self._get_file_metadata(self._full_path(filename))
        assert bool(md), f"File {filename} not found"
        fd = self.client.file_open(flags="0x0002", fileid=md["fileid"])
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

    # recursive variant manually
    def listdir(self):
        directories, files = [], []
        def _listdir(folderid):
            folder_details = self.client.listfolder(folderid=folderid)
            for entry in folder_details["metadata"]["contents"]:
                if entry["isfolder"]:
                    directories.append(PCloudEntry(name=entry["name"], id=entry["folderid"], parent_folder_id=entry["parentfolderid"], raw=entry))
                    _listdir(folderid=entry["folderid"])
                else:
                    files.append(PCloudEntry(name=entry["name"], id=entry["fileid"], parent_folder_id=entry["parentfolderid"], raw=entry))
            return directories,files

        return _listdir(folderid=0)


    # TODO
    # currently ignores directories and duplicate files
    def _get_file_metadata(self, filename):
        splitted_filename = self._full_path(filename).split("/")
        directories,files = self.listdir()
#        found_entries = []
        for f in files:
            if splitted_filename[-1]== f.name:
#                found_entries.append(f)
                return f.raw
#        if len(splitted_filename) == 2 and len(found_entries) == 1:
#            return found_entries[0].raw
#        for entry in found_entries:
#            print(entry)
#            parent = entry.parentfolderid
#            for d in directories:
#                if d.id == parentfolderid and d.name == splitted_filename[-2]:
#                    print("ok")

        raise FileNotFoundException(f"File {filename} not found")



    """
    def get_ids(self, data, key):
        stack = [data]
        result = []
        while stack:
            elem = stack.pop()
            if isinstance(elem, dict):
                for k, v in elem.items():
                    if k == key:
                        result.append(v)
                    if isinstance(elem, (list, dict)):
                        stack.append(v)
            elif isinstance(elem, list):
                for obj in elem:
                    stack.append(obj)
        return result

    def get_file_id_by_filename(self, filename):
        splitted_filename = self._full_path(filename).split("/")
        result = self.client.listfolder(folderid=0, recursive=True)
        print(result)
        values = self.get_ids(result["metadata"], "name")
        if splitted_filename[-1] in values:
            print(filename)
#        import jmespath
#        print(jmespath.search(f'{"name": "{filename}"}'))
#        from nested_lookup import nested_lookup
#        print(nested_lookup('name', result))
#        print(result)
#        for f in files:
#            if f.name == splitted_filename[-1]:
#                if len(splitted_filename) == 1:
#                    return f.id
#        raise FileNotFoundException(f"File {filename} not found")
    """


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


