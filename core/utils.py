import uuid

from django.utils.text import slugify


def generate_uuid() -> str:
    """
    Generate a random UUID string.
    """
    return str(uuid.uuid4())


def slugify_text(text: str, allow_unicode: bool = True) -> str:
    """
    Return a slugified version of the given text.
    """
    return slugify(text, allow_unicode=allow_unicode)


def chunk_list(data, chunk_size: int):
    """
    Yield successive chunk_size-sized chunks from list.
    """
    for i in range(0, len(data), chunk_size):
        yield data[i : i + chunk_size]
