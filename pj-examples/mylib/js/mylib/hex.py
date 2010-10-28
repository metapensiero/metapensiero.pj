

def hex_encode_256(n):
    if n == 0:
        result = '00'
    elif 0 <= n <= 15:
        result = '0' + n.toString(16)
    else:
        result = n.toString(16)
    return result


