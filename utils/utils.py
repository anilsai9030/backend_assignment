from email.utils import parseaddr


def chunker(l, n):
    """Yield successive n-sized chunks from list
    l = list to be chunked
    n = chunk size
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]


def extract_email(from_value):
    name, email = parseaddr(from_value)
    return email
