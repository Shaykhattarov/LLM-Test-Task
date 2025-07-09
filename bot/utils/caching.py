import hashlib


def generate_cache_key(text: str):
    """ Генерация уникального ключа для кеша """
    return hashlib.sha256(text.encode()).hexdigest()