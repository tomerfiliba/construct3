import unittest
from construct3 import (byte, int8, int16ub, int16ul, int16sb, int16sl, int32ub, int32sb, int32ul, int32sl,
    int64ub, int64sb, int64ul, int64sl, float32l, float32b, float64l, float64b)


class TestNumbers(unittest.TestCase):
    def test_builtins(self):
        self.assertEqual(byte.unpack("\x88"), 0x88)
        self.assertEqual(int8.unpack("\x88"), 0x88 - 0x100)
        self.assertEqual(int16ub.unpack("\x88\x77"), 0x8877)
        self.assertEqual(int16sb.unpack("\x88\x77"), 0x8877-0x10000)
        self.assertEqual(int16ul.unpack("\x77\x88"), 0x8877)
        self.assertEqual(int16sl.unpack("\x77\x88"), 0x8877-0x10000)
        self.assertEqual(int32ub.unpack("\x88\x77\x66\x55"), 0x88776655)
        self.assertEqual(int32sb.unpack("\x88\x77\x66\x55"), 0x88776655-0x100000000)
        self.assertEqual(int32ul.unpack("\x55\x66\x77\x88"), 0x88776655)
        self.assertEqual(int32sl.unpack("\x55\x66\x77\x88"), 0x88776655-0x100000000)
        self.assertEqual(int64ub.unpack("\x88\x77\x66\x55\x44\x33\x22\x11"), 0x8877665544332211)
        self.assertEqual(int64sb.unpack("\x88\x77\x66\x55\x44\x33\x22\x11"), 0x8877665544332211-0x10000000000000000)
        self.assertEqual(int64ul.unpack("\x11\x22\x33\x44\x55\x66\x77\x88"), 0x8877665544332211)
        self.assertEqual(int64sl.unpack("\x11\x22\x33\x44\x55\x66\x77\x88"), 0x8877665544332211-0x10000000000000000)
        self.assertAlmostEqual(float32b.unpack("\x41\x02\x02\x02"), 8.1254901886)
        self.assertAlmostEqual(float32l.unpack("\x02\x02\x02\x41"), 8.1254901886)


if __name__ == "__main__":
    unittest.main()


