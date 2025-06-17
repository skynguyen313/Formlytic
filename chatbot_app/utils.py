import os
import re
from django.core.files.storage import FileSystemStorage

class CustomStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):

        if not self.exists(name):
            return name

        base, ext = os.path.splitext(name)

        match = re.search(r'\((\d+)\)$', base)
        if match:
            counter = int(match.group(1)) + 1
            base = re.sub(r'\(\d+\)$', f'({counter})', base)
        else:
            base = f'{base}(1)'

        while self.exists(f'{base}{ext}'):
            match = re.search(r'\((\d+)\)$', base)
            if match:
                counter = int(match.group(1)) + 1
                base = re.sub(r'\(\d+\)$', f'({counter})', base)
            else:
                base = f'{base}(1)'

        return f'{base}{ext}'