
def jit(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

def vectorize(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

prange = range
float64 = float
