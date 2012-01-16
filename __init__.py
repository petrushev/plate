
from hashlib import md5 as hashlib_md5

def md5(text):
    if type(text)==unicode:
        text = text.encode('utf-8')
    text = str(text)
    m = hashlib_md5(text)
    return m.hexdigest()

