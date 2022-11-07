import random 
import string 
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

class Authenticator:
    
    @staticmethod
    def hash_password(password: str) -> str :
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool :
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def generate_random_password(length: int = 12) -> str :
        return ''.join(random.choice(string.ascii_letters + string.digits + '-_') for i in range(length))
        