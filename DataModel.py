import sys
import mmap

class Observer:
    def update_geometry(self):
        NotImplementedError('method not implemented.')

class DataModel(object, Observer):
    def __init__(self, data):
        self._dataOffset = 0
        self.rows = self.cols = 0
        self.data = data
        self._lastOffset = 0

    @property
    def dataOffset(self):
        return self._dataOffset
    
    @dataOffset.setter
    def dataOffset(self, value):
        self._lastOffset = self._dataOffset
        self._dataOffset = value

    def getLastOffset(self):
        return self._lastOffset

    def inLimits(self, x):
        if x >= 0 and x < len(self.data):
            return True

        return False

    def slide(self, off):
        if self.inLimits(self.dataOffset + off):
            self.dataOffset += off

    def goTo(self, off):
        if self.inLimits(off):
            self.dataOffset = off

    def offsetInPage(self, off):
        if off >= self.dataOffset and off <= self.dataOffset + self.rows*self.cols:
            return True

        return False

    def update_geometry(self, rows, cols):
        self.rows = rows
        self.cols = cols

    def slideLine(self, factor):
        self.slide(factor*self.cols)

    def slidePage(self, factor):
        self.slide(factor*self.cols*self.rows)

    def slideToLastPage(self):
        if self.rows*self.cols > len(self.data):
            return

        self.dataOffset = len(self.data) - self.cols*self.rows

    def slideToFirstPage(self):
        self.dataOffset = 0

    def getXYInPage(self, off):
        off -= self.dataOffset
        x, y = off/self.cols, off%self.cols
        return x, y

    def getPageOffset(self, page):
        return self.getOffset() + (page)*self.rows*self.cols


    def getQWORD(self, offset, asString=False):
        if offset + 8 > len(self.data):
            return None

        b = bytearray(self.data[offset:offset+8])

        d = ((b[7] << 56) | (b[6] << 48) | (b[5] << 40) | (b[4] << 32) | (b[3] << 24) | (b[2] << 16) | (b[1] << 8) | (b[0])) & 0xFFFFFFFFFFFFFFFF

        if not asString:        
            return d

        s = '{0:016X}'.format(d)
        
        return s

    def getDWORD(self, offset, asString=False):
        if offset + 4 >= len(self.data):
            return None

        b = bytearray(self.data[offset:offset+4])

        d = ((b[3] << 24) | (b[2] << 16) | (b[1] << 8) | (b[0])) & 0xFFFFFFFF

        if not asString:        
            return d

        s = '{0:08X}'.format(d)
        
        return s

    def getWORD(self, offset, asString=False):
        if offset + 2 > len(self.data):
            return None

        b = bytearray(self.data[offset:offset+2])

        d = ((b[1] << 8) | (b[0])) & 0xFFFF

        if not asString:        
            return d

        s = '{0:04X}'.format(d)
        
        return s

    def getBYTE(self, offset, asString=False):
        if offset + 1 > len(self.data):
            return None

        b = bytearray(self.data[offset:offset+1])

        d = (b[0]) & 0xFF

        if not asString:        
            return d

        s = '{0:02X}'.format(d)
        
        return s

    def getChar(self, offset):
        if offset < 0:
            return None

        if offset >= len(self.data):
            return None

        return self.data[offset]

    def getStream(self, start, end):
        return bytearray(self.data[start:end])

    def getOffset(self):
        return self.dataOffset

    def getData(self):
        return self.data

    def getDataSize(self):
        return len(self.data)

    @property
    def source(self):
        return ''

    def flush(self):
        raise NotImplementedError('method not implemented.')

    def write(self):
        raise NotImplementedError('method not implemented.')

    def close(self):
        pass

class FileDataModel(DataModel):
    def __init__(self, filename):
        self._filename = filename

        self._f = open(filename, "r+b")

        # memory-map the file, size 0 means whole file
        self._mapped = mmap.mmap(self._f.fileno(), 0, access=mmap.ACCESS_COPY)

        super(FileDataModel, self).__init__(self._mapped)

    @property
    def source(self):
        return self._filename

    def flush(self):
        self._f.write(self._mapped)

    def close(self):
        self._mapped.close()
        self._f.close()

    def write(self, offset, stream):
        self._mapped.seek(offset)
        self._mapped.write(stream)
