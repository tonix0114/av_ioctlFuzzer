from pyZZUF import *
import os
import ZIP_fuzz 
import zlib
# import fuzz_utils


class Compress_FUZZ:

    def __init__(self, seed_dir, out_dir, filename):
    
        self.SEED_DIR = seed_dir
        self.OUT_DIR = out_dir  
        self.FILENAME = filename
        self.INPUT = ""
        self.NEW_DATA = ""
        f = open(self.SEED_DIR + self.FILENAME, "rb")
        self.INPUT = f.read()

    def write_file(self):

        ext = self.FILENAME.split(".")[1]
    
        if(ext == "zip"):
            self.NEW_DATA = self.zip_fuzz()
            
        elif(ext == "gz"):
            self.NEW_DATA = self.gzip2_fuzz()
            
        elif(ext == "7z"):
            self.NEW_DATA = self.sevenzip_fuzz()
            
        elif(ext == "rar"):
            self.NEW_DATA = self.rar_fuzz()

        else:
            self.NEW_DATA = None

        if(self.NEW_DATA != None):       
            f = open(self.OUT_DIR + self.FILENAME, "wb")
            f.write(self.NEW_DATA)
        
    def zip_fuzz(self):
        
        file_path = self.SEED_DIR + self.FILENAME
        return ZIP_fuzz.main(self.SEED_DIR, self.OUT_DIR, self.FILENAME)
        

    def gzip_fuzz(self):
        
        length = len(self.INPUT)
        SIGN = self.INPUT[:2]
        CHECKSUM = self.INPUT[length-8:length-4]
        FILESIZE = self.INPUT[length-4:]

        zzbuf = pyZZUF(self.INPUT[2:-8])

        rdata = ""
        rdata += SIGN
        rdata += zzbuf.mutate().tostring()
        rdata += CHECKSUM
        rdata += FILESIZE

        return rdata    

    def sevenzip_fuzz(self):   # so dirty......
    
        SIGN = self.INPUT[:6]

        zzbuf = pyZZUF(self.INPUT[6:])

        rdata = ""
        rdata += SIGN
        rdata += zzbuf.mutate().tostring()

        return rdata

# def tar_fuzz(self):


    def rar_fuzz(self):
    
        SIGN = self.INPUT[:0x5]
        HEADER_SIZE = self.INPUT[0x5:0x7]
        FILE_CHECKSUM = self.INPUT[0x24:0x28]
        BHEADER_SIZE = self.INPUT[0x19:0x1b]
        HEAD_TYPE1 = chr(0x73)
        HEAD_TYPE2 = chr(0x74)

        fuzzed_data = pyZZUF(self.INPUT).mutate().tostring()

        rdata = ""
        rdata += SIGN
        rdata += HEADER_SIZE
        
        tmp_data = HEAD_TYPE1
        tmp_data += fuzzed_data[0xa:0x14]

        HEADER_CRC = zlib.crc32(tmp_data) & 0xffffffff
        rdata += chr(HEADER_CRC & 0xff)
        rdata += chr((HEADER_CRC >> 8) & 0xff)
        rdata += tmp_data
        
        size = ord(BHEADER_SIZE[0]) + 0xff * ord(BHEADER_SIZE[1])
        tmp_data = HEAD_TYPE2
        tmp_data += fuzzed_data[0x17:0x19]
        tmp_data += BHEADER_SIZE
        tmp_data += fuzzed_data[0x1b:0x24]
        tmp_data += FILE_CHECKSUM
        tmp_data += fuzzed_data[0x28:0x14+size]
        
        BHEADER_CRC = zlib.crc32(tmp_data) & 0xffffffff
        
        rdata += chr(BHEADER_CRC & 0xff)
        rdata += chr((BHEADER_CRC >> 8) & 0xff)
        rdata += tmp_data
        
        rdata += fuzzed_data[0x14+size:-7]
        
        END_CRC = self.INPUT[-7:]
        rdata += END_CRC
         
        return rdata

    

seed_dir = "C:\\Users\\JungUn\\Desktop\\seedfolder\\"
out_dir = "C:\\Users\\JungUn\\Desktop\\outfolder\\"
filelist = os.listdir(seed_dir)

for filename in filelist:

    fuzzer = Compress_FUZZ(seed_dir, out_dir, filename)
    fuzzer.write_file()
