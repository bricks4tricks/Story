class Error(Exception):
    pass

class extras:
    class RealDictCursor:
        pass

def connect(*args, **kwargs):
    raise NotImplementedError("Database not available")
