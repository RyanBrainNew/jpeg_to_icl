from crcmod.predefined import mkPredefinedCrcFun

class Hex_Writer(object):
    def __init__(self):
        super(Hex_Writer, self).__init__()
        self.name= b'\x44\x47\x55\x53\x5f\x33'        # 地址0x0000 长度6 固定名称DGUS_3
        self.crc=b'\x00\x00'                          # 地址0x0006 长度2 文件的CRC校验值
        self.data_len=0                               # 地址0x0008 长度4 文件的总字节长度-8
        self.jpeg = b'\x04'                           # 地址0x000C 长度1 JPEG图标（图片）ICL文件
        self.jpeg_maxindex = b'\x00\x00'              # 地址0x000D 长度2 文件中的最大图标ID
        self.encrypt = b'\x00'                        # 地址0x000F 长度1 加密标记
        self.icon_addindex = b'\x00\x00\x00\x14'      # 地址0x0010 长度N*4 JPEG数据保存索引地址，4Bytes
        self.jpeg_xresolution = b'\x04\x00'           # 地址0x00   长度2 图标X分辨率
        self.jpeg_yresolution = b'\x02\x58'           # 地址0x02   长度2 图标Y分辨率
        self.jpeg_header_len = 0                      # 地址0x04   长度2 JPEG文件头长度，最大0x8000 32KB 找到SOS（FF DA）第一节的终点位置，SOS后的两字节标识长度
        self.jpeg_file_len = 0                        # 地址0x06   长度4 JPEG文件大小, 4Bytes
        self.jpeg_bytes = 0                           # 地址0x0A   JPEG数据开始
        self.jpeg_total_filelen = 0                   # 这个变量只是用来存放图片总长度使用

    def update_data_len(self):
        self.data_len = (self.jpeg_total_filelen + 16 + 4 + 10 - 8).to_bytes(4,"big")
        return

if __name__=='__main__':
    
    # 初始化操作对象
    w=Hex_Writer()
    
    # 读图片数据 图片命名需要以00_等序号开始
    file = open(r'pic/00_1.jpg', 'br')
    w.jpeg_bytes = file.read()
    w.jpeg_total_filelen = len(w.jpeg_bytes)
    file.close()
    
    # 查找SOS起始位置
    sos_index = w.jpeg_bytes.find(b'\xff\xda')
    # 寻找SOS的长度标识
    sos_len = w.jpeg_bytes[sos_index+3]
    # 定位SOS结束位置
    # 例如SOS段数据起始为FF DA 00 0C，上面取的是FF位置，实际从0C之后开始计算，最后需要+3，。因为下面公式中的变量都是地址，实际长度需要+1
    jpeg_header_len = sos_index + sos_len + 3 + 1
    jpeg_total_len = len(w.jpeg_bytes)
    jpeg_file_len = (jpeg_total_len -jpeg_header_len)

    w.jpeg_header_len = jpeg_header_len.to_bytes(2, "big")
    w.jpeg_file_len = jpeg_file_len.to_bytes(4,"big")

    w.update_data_len()
    
    # 使用PyCRC库创建CRC16的预定义函数
    crc16 = mkPredefinedCrcFun('modbus')
    # 要计算CRC16校验码的数据
    test_bytes = b''.join([w.data_len, w.jpeg, w.jpeg_maxindex, w.encrypt, w.icon_addindex, w.jpeg_xresolution, w.jpeg_yresolution, w.jpeg_header_len, w.jpeg_file_len, w.jpeg_bytes])
    # 计算CRC16校验码
    crc_value = crc16(test_bytes)
    # 打印CRC16校验码
    # print('CRC16:', hex(crc_value))
    # icl文件的crc值与该算法算出的高低位相反，此处进行高低位倒置
    data = crc_value
    reversed_data = ((data & 0xff) << 8) | ((data >> 8) & 0xff)
    crc = reversed_data.to_bytes(2, "big")
    w.crc = crc
    
    # 将多个字节变量拼接为一个字节串
    # byte_data = b''.join([w.name, w.crc, w.data_len, w.jpeg, w.jpeg_maxindex, w.encrypt, w.icon_addindex, w.jpeg_xresolution, w.jpeg_yresolution, w.jpeg_header_len, w.jpeg_file_len, w.jpeg_bytes])
    byte_data = b''.join([w.name, w.crc, test_bytes])
    
    # 打开二进制写入模式的文件
    with open('23_mytest.icl', 'wb') as f:
        # 将拼接后的字节数据写入文件中
        f.write(byte_data)
    
    # 输出提示信息
    print('Done!')