import zlib, io
import numpy as np
import requests

def encode_data(nparr):
    """
    Returns the given numpy array as compressed bytestring,
    the uncompressed and the compressed byte size.
    """
    bytestream = io.BytesIO()
    np.save(bytestream, nparr)
    uncompressed = bytestream.getvalue()
    # compressed = zlib.compress(uncompressed)
    compressed = uncompressed
    return compressed

def decode_data(bytestring):
    """
    """
    #return np.load(io.BytesIO(zlib.decompress(bytestring)))
    return np.load(io.BytesIO(bytestring))


def post_encoded(url, data):
    encoded = encode_data(data)

    return requests.post(url, data=encoded, headers={'Content-Type': 'application/octet-stream'})

def post_decode(request):
    data = decode_data(request.data)

    data = data[()]

    return data
