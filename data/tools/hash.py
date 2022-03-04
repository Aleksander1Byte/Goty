def generate_hash():
    import random
    hash = random.getrandbits(128)
    return "%032x" % hash
