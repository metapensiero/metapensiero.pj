

def bind(f, obj):
    return lambda: f.apply(obj, arguments)

