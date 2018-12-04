import re
from urllib.parse import urljoin

from django.core.files.storage import FileSystemStorage
from django.utils.encoding import filepath_to_uri


class JourneyLogDefaultStorage(FileSystemStorage):
    def __init__(self, location=None):
        super(JourneyLogDefaultStorage, self).__init__(location)

    def url(self, name):
        url = filepath_to_uri(name)
        if url is not None:
            url = url.lstrip('/')

        if re.match(r'^public/', url):
            return urljoin(self.base_url, re.sub(r'^public/', '', url))
        else:
            return None
