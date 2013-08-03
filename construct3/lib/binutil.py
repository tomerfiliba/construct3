import six


empty = six.b("")

if six.PY3:
    def num_to_bits(number, width = 32):
        number = int(number)
        if number < 0:
            number += 1 << width
        i = width - 1
        bits = bytearray(width)
        while number and i >= 0:
            bits[i] = number & 1
            number >>= 1
            i -= 1
        return bits
    
    _bitarr = six.b("01")
    def bits_to_num(bits, signed = False):
        bits = bytes(_bitarr[b & 1] for b in bits)
        if signed and bits[0] == 49:
            bits = bits[1:]
            bias = 1 << len(bits)
        else:
            bias = 0
        return int(bits, 2) - bias
    
    _to_bits = [0] * 256
    _to_bytes = {}
    for i in range(256):
        bits = bytes(num_to_bits(i, 8))
        _to_bits[i] = bits
        _to_bytes[bits] = i
    
    def bytes_to_bits(data):
        return empty.join(_to_bits[int(b)] for b in data)
    
    def bits_to_bytes(bits):
        if len(bits) & 7:
            raise ValueError("The length of `bits` must be a multiple of 8")
        return bytes(_to_bytes[bits[i:i+8]] for i in range(0, len(bits), 8))
    
    byte_to_int = int
    def int_to_byte(num):
        return bytes((num,)) 

    def swap_bytes(bits, bytesize=8):
        i = 0
        l = len(bits)
        output = bytearray((l // bytesize) + bool(l & 7))
        j = len(output) - 1
        while i < l:
            output[j] = bits[i : i + bytesize]
            i += bytesize
            j -= 1
        return output
else:
    def num_to_bits(number, width = 32):
        number = int(number)
        if number < 0:
            number += 1 << width
        i = width - 1
        bits = ["\x00"] * width
        while number and i >= 0:
            bits[i] = "\x00\x01"[number & 1]
            number >>= 1
            i -= 1
        return "".join(bits)
    
    def bits_to_num(bits, signed = False):
        bits = "".join("01"[ord(b) & 1] for b in bits)
        if signed and bits[0] == "1":
            bits = bits[1:]
            bias = 1 << len(bits)
        else:
            bias = 0
        return int(bits, 2) - bias
    
    _to_bits = [0] * 256
    _to_bytes = {}
    for i in range(256):
        bits = num_to_bits(i, 8)
        _to_bits[i] = bits
        _to_bytes[bits] = chr(i)
    
    def bytes_to_bits(data):
        return "".join(_to_bits[ord(b)] for b in data)
    
    def bits_to_bytes(bits):
        if len(bits) & 7:
            raise ValueError("The length of `bits` must be a multiple of 8")
        return "".join(_to_bytes[bits[i:i+8]] for i in range(0, len(bits), 8))
    
    byte_to_int = ord
    int_to_byte = chr

    def swap_bytes(bits, bytesize=8):
        i = 0
        l = len(bits)
        output = [""] * ((l // bytesize) + 1)
        j = len(output) - 1
        while i < l:
            output[j] = bits[i : i + bytesize]
            i += bytesize
            j -= 1
        return "".join(output)


class BitStreamReader(object):
    __slots__ = ["stream", "buffer"]
    def __init__(self, stream):
        self.stream = stream
        self.buffer = empty
    def read(self, count):
        if count == 0:
            return empty
        if count > len(self.buffer):
            extra = count - len(self.buffer)
            data = self.stream.read(extra // 8 + bool(extra & 7))
            self.buffer += bytes_to_bits(data)
        buf = self.buffer[:count]
        self.buffer = self.buffer[count:]
        return buf
    def close(self):
        if self.buffer:
            raise ValueError("Not all data has been consumed (it must sum up to whole bytes)", self.buffer)

class BitStreamWriter(object):
    __slots__ = ["stream", "buffer"]
    def __init__(self, stream):
        self.stream = stream
        self.buffer = empty
    def write(self, bits):
        self.buffer += bits
    def flush(self, force_all = False):
        if not self.buffer:
            return
        if force_all and len(self.buffer) & 7:
            raise ValueError("Written data must sum up to whole bytes (got %r bits)" % (len(self.buffer,)))
        count = (len(self.buffer) >> 3) << 3
        bits = self.buffer[:count]
        self.buffer = self.buffer[count:]
        self.stream.write(bits_to_bytes(bits))
    def close(self):
        self.flush(True)

_printable = ["."] * 256
_printable[32:128] = [chr(i) for i in range(32, 128)]

def hexdump(data, linesize = 16):
    dumped = []
    if len(data) < 65536:
        fmt = "%%04X   %%-%ds   %%s"
    else:
        fmt = "%%08X   %%-%ds   %%s"
    fmt = fmt % (3 * linesize - 1,)
    for i in range(0, len(data), linesize):
        line = data[i : i + linesize]
        hextext = " ".join('%02x' % (byte_to_int(b),) for b in line)
        rawtext = "".join(_printable[byte_to_int(b)] for b in line)
        dumped.append(fmt % (i, str(hextext), str(rawtext)))
    return "\n".join(dumped)


if __name__ == "__main__":
    assert bits_to_num(num_to_bits(17, 8)) == 17 
    assert bits_to_num(num_to_bits(128, 8)) == 128 
    assert bits_to_num(num_to_bits(255, 8), signed = True) == -1
    assert bits_to_bytes(bytes_to_bits(six.b("ABC"))) == six.b("ABC")
    print(hexdump("hello world what is the up? how\t\r\n\x00\xff are we feeling today?!", 16))







