from base64 import urlsafe_b64decode
from base64 import urlsafe_b64encode
from uuid import UUID




class ID:

    @staticmethod
    def uuid2slug(uuid_string: str):
        try: 
            return urlsafe_b64encode(UUID(uuid_string).bytes).rstrip(b'=').decode('ascii')
        except: 
            return None

    @staticmethod
    def slug2uuid(slug: str):
        try: 
            return str(UUID(bytes=urlsafe_b64decode(slug + '==')))
        except:
            return -1
