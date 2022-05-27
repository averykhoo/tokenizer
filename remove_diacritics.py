import unicodedata

from tokenizer import is_text_combining_char


def remove_diacritics(text: str) -> str:
    """
    Remove diacritics or zalgo from a string.
    """
    return ''.join(char for char in unicodedata.normalize('NFKD', text)
                   if not is_text_combining_char(char))
