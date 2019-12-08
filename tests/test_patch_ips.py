import unittest
import binascii
import os
from lazy_ips.patch import ips
from shutil import copyfile

in_file = "./tests/src.bin"
out_file = "./tests/out.bin"
patch_file = "./tests/patch.ips"
out_crc = "6325E788"


def crc(filename):
    with open(filename, 'rb') as f:
        buf = f.read()
        buf = (binascii.crc32(buf) & 0xFFFFFFFF)
        return "%X" % buf


class TestPatchIPS(unittest.TestCase):
    def setUp(self):
        copyfile(in_file, out_file)

    def tearDown(self):
        if os.path.exists(out_file):
            os.remove(out_file)

    def test_apply_patch(self):
        with open(out_file, 'rb+') as out, open(patch_file, 'rb') as patch:
            for patch_line in ips.read_patch(patch):
                ips.apply_patch_line(out, patch_line)

        self.assertEqual(crc(out_file), out_crc)


if __name__ == '__main__':
    unittest.main()
