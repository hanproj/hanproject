#! C:\Python36\
# -*- encoding: utf-8 -*-
import os

utf8_bom_b = b'\xef\xbb\xbf'

def readlines_of_utf8_file(filename):
    funct_name = 'readlines_of_utf8_file()'
    retval = []
    if not os.path.isfile(filename):
        print(funct_name + u' ERROR: filename INVALID: ' + filename)
        return retval
    with open(filename, 'rb') as f:
        line_list = f.readlines()
    line_list[0].replace(utf8_bom_b, b'')
    for line in line_list:
        line = line.decode('utf8')
        line = line.replace('\r\n', '')
        retval.append(line)
    return retval
