from collections import namedtuple
from struct import unpack

PatchLine = namedtuple('PatchLine', ['offset', 'data'])


def read_patch_line(file):
    eof_marker = b'EOF'
    offset_size = 3
    data_len_size = 2
    rle_len_size = 2

    try:
        offset_raw = file.read(offset_size)
        if offset_raw == eof_marker:
            return None
        offset = unpack('>l', b'\x00' + offset_raw)[0]

    except Exception:
        raise IOError("error reading offset")

    try:
        data_len_raw = file.read(data_len_size)
        data_len = unpack('>h', data_len_raw)[0]

        if data_len > 0:
            data = file.read(data_len)
            return PatchLine(offset, data)

        # RLE
        rle_len_raw = file.read(rle_len_size)
        rle_len = unpack('>h', rle_len_raw)[0]
        rle_byte = file.read(1)
        data = rle_byte * rle_len
        return PatchLine(offset, data)

    except Exception:
        raise IOError("error reading data")


def read_patch(file):
    patch_marker = b'PATCH'

    # Check marker.
    data = file.read(len(patch_marker))
    if data != patch_marker:
        raise IOError("unknown format")

    eof = False
    while not eof:
        data = read_patch_line(file)
        if data:
            yield data
        else:
            eof = True


def apply_patch_line(image, patch_line):
    try:
        image.seek(patch_line.offset)
    except Exception:
        image.seek(0, 2)
    image.write(patch_line.data)
