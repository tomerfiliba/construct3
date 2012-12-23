import unittest
from six import b
from construct3 import (byte, int8, int16ub, int16ul, int16sb, int16sl, int32ub, int32sb, int32ul, int32sl,
    int64ub, int64sb, int64ul, int64sl, float32l, float32b, float64l, float64b, int24ul, int24sl, int24ub, int24sb,
    bit, nibble, octet, Bitwise, TwosComplement, MaskedInteger, Padding)


class TestNumbers(unittest.TestCase):
    def test_int8(self):
        self.assertEqual(byte.unpack(b("\x88")), 0x88)
        self.assertEqual(int8.unpack(b("\x88")), 0x88 - 0x100)
        
        self.assertEqual(byte.pack(0x88), b("\x88"))
        self.assertEqual(int8.pack(0x88 - 0x100), b("\x88"))
    
    def test_int16(self):
        self.assertEqual(int16ub.unpack(b("\x88\x77")), 0x8877)
        self.assertEqual(int16sb.unpack(b("\x88\x77")), 0x8877-0x10000)
        self.assertEqual(int16ul.unpack(b("\x77\x88")), 0x8877)
        self.assertEqual(int16sl.unpack(b("\x77\x88")), 0x8877-0x10000)
        
        self.assertEqual(int16ub.pack(0x8877), b("\x88\x77"))
        self.assertEqual(int16sb.pack(0x8877-0x10000), b("\x88\x77"))
        self.assertEqual(int16ul.pack(0x8877), b("\x77\x88"))
        self.assertEqual(int16sl.pack(0x8877-0x10000), b("\x77\x88"))

    def test_int32(self):
        self.assertEqual(int32ub.unpack(b("\x88\x77\x66\x55")), 0x88776655)
        self.assertEqual(int32sb.unpack(b("\x88\x77\x66\x55")), 0x88776655-0x100000000)
        self.assertEqual(int32ul.unpack(b("\x55\x66\x77\x88")), 0x88776655)
        self.assertEqual(int32sl.unpack(b("\x55\x66\x77\x88")), 0x88776655-0x100000000)

        self.assertEqual(int32ub.pack(0x88776655), b("\x88\x77\x66\x55"))
        self.assertEqual(int32sb.pack(0x88776655-0x100000000), b("\x88\x77\x66\x55"))
        self.assertEqual(int32ul.pack(0x88776655), b("\x55\x66\x77\x88"))
        self.assertEqual(int32sl.pack(0x88776655-0x100000000), b("\x55\x66\x77\x88"))

    def test_int64(self):
        self.assertEqual(int64ub.unpack(b("\x88\x77\x66\x55\x44\x33\x22\x11")), 0x8877665544332211)
        self.assertEqual(int64sb.unpack(b("\x88\x77\x66\x55\x44\x33\x22\x11")), 0x8877665544332211-0x10000000000000000)
        self.assertEqual(int64ul.unpack(b("\x11\x22\x33\x44\x55\x66\x77\x88")), 0x8877665544332211)
        self.assertEqual(int64sl.unpack(b("\x11\x22\x33\x44\x55\x66\x77\x88")), 0x8877665544332211-0x10000000000000000)

        self.assertEqual(int64ub.pack(0x8877665544332211), b("\x88\x77\x66\x55\x44\x33\x22\x11"))
        self.assertEqual(int64sb.pack(0x8877665544332211-0x10000000000000000), b("\x88\x77\x66\x55\x44\x33\x22\x11"))
        self.assertEqual(int64ul.pack(0x8877665544332211), b("\x11\x22\x33\x44\x55\x66\x77\x88"))
        self.assertEqual(int64sl.pack(0x8877665544332211-0x10000000000000000), b("\x11\x22\x33\x44\x55\x66\x77\x88"))

    def test_float(self):
        self.assertAlmostEqual(float32b.unpack(b("\x41\x02\x02\x02")), 8.1254901886)
        self.assertAlmostEqual(float32l.unpack(b("\x02\x02\x02\x41")), 8.1254901886)
        self.assertAlmostEqual(float64b.unpack(b("\x41\x02\x02\x02\x03\x03\x03\x03")), 147520.25147058823)
        self.assertAlmostEqual(float64l.unpack(b("\x03\x03\x03\x03\x02\x02\x02\x41")), 147520.25147058823)

        self.assertEqual(float32b.pack(8.1254901886), b("\x41\x02\x02\x02"))
        self.assertEqual(float32l.pack(8.1254901886), b("\x02\x02\x02\x41"))
        self.assertEqual(float64b.pack(147520.25147058823), b("\x41\x02\x02\x02\x03\x03\x03\x03"))
        self.assertEqual(float64l.pack(147520.25147058823), b("\x03\x03\x03\x03\x02\x02\x02\x41"))
    
    def test_bits(self):
        self.assertEqual(Bitwise(octet).unpack(b("\x88")), 0x88)
        self.assertEqual(TwosComplement(Bitwise(octet), 8).unpack(b("\x88")), 0x88 - 0x100)
        self.assertEqual(Bitwise(bit >> Padding(2) >> bit >> bit >> Padding(3)).unpack(b("\x88")), [1, 0, 1])
        self.assertEqual(Bitwise(nibble >> nibble).unpack(b("\x87")), [8, 7])

        self.assertEqual(Bitwise(octet).pack(0x88), b("\x88"))
        self.assertEqual(TwosComplement(Bitwise(octet), 8).pack(0x88 - 0x100), b("\x88"))
        self.assertEqual(Bitwise(bit >> Padding(2) >> bit >> bit >> Padding(3)).pack([1, 0, 1]), b("\x88"))
        self.assertEqual(Bitwise(nibble >> nibble).pack([8, 7]), b("\x87"))

        self.assertRaises(ValueError, Bitwise(bit >> bit).unpack, b("\x88"))
        self.assertRaises(ValueError, Bitwise(bit >> bit).pack, [1,1])
    
    def test_int24(self):
        self.assertEqual(int24ub.unpack(b("\x03\x02\x01")), 0x030201)
        self.assertEqual(int24sb.unpack(b("\x03\x02\x01")), 0x030201)
        self.assertEqual(int24ub.unpack(b("\x83\x02\x01")), 0x830201)
        self.assertEqual(int24sb.unpack(b("\x83\x02\x01")), 0x830201 - 0x1000000)
        self.assertEqual(int24ul.unpack(b("\x01\x02\x03")), 0x030201)
        self.assertEqual(int24sl.unpack(b("\x01\x02\x03")), 0x030201)
        self.assertEqual(int24ul.unpack(b("\x01\x02\x83")), 0x830201)
        self.assertEqual(int24sl.unpack(b("\x01\x02\x83")), 0x830201 - 0x1000000)

        self.assertEqual(int24ub.pack(0x030201), b("\x03\x02\x01"))
        self.assertEqual(int24sb.pack(0x030201), b("\x03\x02\x01"))
        self.assertEqual(int24ub.pack(0x830201), b("\x83\x02\x01"))
        self.assertEqual(int24sb.pack(0x830201 - 0x1000000), b("\x83\x02\x01"))
        self.assertEqual(int24ul.pack(0x030201), b("\x01\x02\x03"))
        self.assertEqual(int24sl.pack(0x030201), b("\x01\x02\x03"))
        self.assertEqual(int24ul.pack(0x830201), b("\x01\x02\x83"))
        self.assertEqual(int24sl.pack(0x830201 - 0x1000000), b("\x01\x02\x83"))
    
    def test_maskedint(self):
        self.assertEqual(MaskedInteger(int16ub, lowbyte = (0, 8), highbyte = (8, 8)).unpack(b("\x34\x56")),
            dict(highbyte = 0x34, lowbyte = 0x56))
        self.assertEqual(MaskedInteger(int16ub, lownib = (0, 4), midbyte = (4, 8), highnib = (12, 4)).unpack(b("\x34\x56")),
            dict(highnib = 0x3, midbyte = 0x45, lownib = 0x6))
        self.assertEqual(MaskedInteger(int16ul, lowbyte = (0, 8), highbyte = (8, 8)).unpack(b("\x56\x34")),
            dict(highbyte = 0x34, lowbyte = 0x56))
        self.assertEqual(MaskedInteger(int16ul, lownib = (0, 4), midbyte = (4, 8), highnib = (12, 4)).unpack(b("\x56\x34")),
            dict(highnib = 0x3, midbyte = 0x45, lownib = 0x6))

        self.assertEqual(MaskedInteger(int16ub, lowbyte = (0, 8), highbyte = (8, 8)).pack(dict(highbyte = 0x34, lowbyte = 0x56)),
            b("\x34\x56"))
        self.assertEqual(MaskedInteger(int16ub, lownib = (0, 4), midbyte = (4, 8), highnib = (12, 4)).pack(
            dict(highnib = 0x3, midbyte = 0x45, lownib = 0x6)), b("\x34\x56"))
        self.assertEqual(MaskedInteger(int16ul, lowbyte = (0, 8), highbyte = (8, 8)).pack(dict(highbyte = 0x34, lowbyte = 0x56)),
            b("\x56\x34"))
        self.assertEqual(MaskedInteger(int16ul, lownib = (0, 4), midbyte = (4, 8), highnib = (12, 4)).pack(
            dict(highnib = 0x3, midbyte = 0x45, lownib = 0x6)), b("\x56\x34"))


if __name__ == "__main__":
    unittest.main()


