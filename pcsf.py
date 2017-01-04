import crcmod
import sys
import struct
import zlib

HEADER_SIG = bytes([255, 0, 254, 1])
HEADER_LEN = 16
HEADER_VERSION = bytes([0, 0, 0, 3])

# '<<ClientClient>>?VoxelTerrain'
TERRAIN_MARK = [0x3C, 0x3C, 0x43, 0x6C, 0x69, 0x65, 0x6E, 0x74, 0x43, 0x6C, 0x69, 0x65, 0x6E,
    0x74, 0x3E, 0x3E, 0xF3, 0x56, 0x6F, 0x78,0x65, 0x6C, 0x54, 0x65, 0x72, 0x72, 0x61, 0x69, 0x6E, 0x00]


class PlanetCoasterSaveFile():
    def __init__(self, fn):
        self.raw_data = None
        self.body = None
        self.header = { }
        self.terrain_start = -1

        self.crc_func = crcmod.mkCrcFun(0x104C11DB7, 0, True, 0)
        self.read_compressed_file(fn)
        self.parse_raw_data()

    def read_compressed_file(self, fn):
        f = open(fn, 'rb')
        self.raw_data = zlib.decompress(f.read(), -15)
        self.body = [ b for b in self.raw_data[16:] ]
        f.close()

    def parse_raw_data(self):
        self.parse_header(self.raw_data[0:HEADER_LEN])
        body = self.raw_data[HEADER_LEN:]        
        assert(self.header['body_len'] == len(body))
        crc = self.crc_func(body)
        assert(crc == self.header['crc'])

    def create_raw_data(self):
        body = bytes(self.get_body())
        crc = struct.pack('>I', self.crc_func(body))
        body_len = struct.pack('>I', self.header['body_len'])
        return HEADER_SIG + crc + HEADER_VERSION + body_len + body

    def write_raw_file(self, fn):
        out = self.create_raw_data()
        f_out = open(fn, 'wb')
        f_out.write(out)
        f_out.close()        

    def parse_header(self, h):
        assert h[0:4] == HEADER_SIG
        self.header['crc'] = int.from_bytes(h[4:8], byteorder='big')
        assert h[8:12] == HEADER_VERSION
        self.header['body_len'] = int.from_bytes(h[12:16], byteorder='big')

    def get_body(self):        
        return self.body

    def find_terrain(self):
        self.terrain_start = -1
        tm_len = len(TERRAIN_MARK)        
        for i in range(0, len(self.body)):
            if self.body[i : i + tm_len] == TERRAIN_MARK:
                self.terrain_start = i + tm_len
                break
        return self.terrain_start

    def output_file(self, fn):
        out = self.create_raw_data()
        compressor = zlib.compressobj(level=4, method=zlib.DEFLATED, wbits=-15)
        f_out = open(fn, 'wb')
        f_out.write(compressor.compress(out))
        f_out.write(compressor.flush(zlib.Z_FINISH))
        f_out.close()

    def set_byte(self, value, abspos=None, bodypos=None):
        if abspos is not None:
            self.body[bodypos - HEADER_LEN] = b
        elif bodypos is not None:
            self.body[bodypos] = b
