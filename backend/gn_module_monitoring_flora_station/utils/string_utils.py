import re
import unicodedata


def clean_string(dirty_string):
    
    cleaned_string = dirty_string.strip()

    cleaned_string = "".join(
        c for c in unicodedata.normalize("NFD", cleaned_string) if unicodedata.category(c) != "Mn"
    )

    chars_to_replace = "/;, "
    for c in chars_to_replace:
        cleaned_string = cleaned_string.replace(c, "_")

    chars_to_remove = "."
    for c in chars_to_remove:
        cleaned_string = cleaned_string.replace(c, "")

    return cleaned_string


def strip_html(data):
    """
    Retire les balises HTML d'une chaîne.
    """
    p = re.compile(r"<.*?>")
    return p.sub("", data)