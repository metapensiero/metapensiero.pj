## requires: python_version >= (3,6)

def test():

    s = 'a'
    d = {'s': s}
    return f"{s} == {d['s']}"
