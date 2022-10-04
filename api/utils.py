import magic

def guess_ext(data):
    return magic.Magic(extension=True).from_buffer(data).split("/")[0]

def pick_ext(choices):
    for e in choices:
        if e.isalnum() and len(e) <= 5:
            return f".{e}"
    else:
        return ""
