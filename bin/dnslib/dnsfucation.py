# -*- coding:utf-8 -*-
import logging
import sys

logging.basicConfig(level=logging.INFO)


def searchKeyIp(string, dict_data):
    string = string[:-1]
    if string in dict_data.keys():
        return dict_data[string]
    else:
        domain = string.split('.')
        while len(domain) > 2:
            domain = domain[1:]
            b = '*.' + '.'.join(domain)
            if b in dict_data.keys():
                return dict_data[b]
        return None


def hex2Ascii(string):
    try:
        Int = int(string, 16)
        return chr(Int)
    except Exception as e:
        logging.warn("hex2Ascii info:\t%s" % e)


def hex2StrDec(string):
    try:
        return str(int(string, 16))
    except Exception as e:
        logging.warn("hex2StrDec info:\t%s" % e)


def hexIP2DecIP(string):
    string = string.replace('\t', '').replace('\n', '').replace(' ', '')
    try:
        if len(string) == 8:
            return hex2StrDec(string[0:2]) \
                   + "." + hex2StrDec(string[2:4]) \
                   + "." + hex2StrDec(string[4:6]) \
                   + "." \
                   + hex2StrDec(string[6:8]).replace('\t', '').replace('\n', '').replace(' ', '')
        else:
            return "?.?.?.?"
    except Exception as e:
        logging("HexIP2DecIP  info:\t%s" % e)


def dnsHexToDomain(string, start=24, end=26):
    '''原始数据：域名指针默认在24-26个字节位置，
    若不是完整的原始数据，请指定域名指针的位置'''

    try:
        Domain = []
        while string[start:end] != "00" and string[start:end] != "c0":
            n = 0
            i = int(string[start:end], 16)
            while n < i:
                start = end
                end += 2
                Domain.append(hex2Ascii(string[start:end]))
                n += 1
            Domain.append(".")
            start = end
            end += 2
        return ''.join(Domain), end
    except Exception as e:
        logging.warn("DnshextoDomain info:\t%s" % e)


def ip2Hex(ip):
    zone = ip.split(".")
    HEX = ''
    for i in zone:
        i = hex(int(i)).replace("0x", '')
        if len(i) < 2:
            i = '0' + i
        HEX += i
    return HEX


def byteToHex(bins):
    if sys.version_info < (3, 4):
        return bins.encode('hex')
    else:
        return ''.join(["%02X" % x for x in bins]).strip()

def hexToByte(hexStr):
    if sys.version_info < (3, 4):
        return hexStr.decode('hex')
    return bytes.fromhex(hexStr)


def analysis(data, dict_data):
    '''构造DNS报文'''
    data = byteToHex(data)
    domain, end = dnsHexToDomain(data)

    ip = None
    if len(domain) > 0:
        ip = searchKeyIp(domain, dict_data)
        logging.info("Query domain:%s\tip:%s", domain, ip)
    if ip:
        if data[end + 2:end + 4] == '1c':
            '''屏蔽IPv6'''
            data = data[0:4] + '81800001000000000000' + data[24:end] + '001c0001'
            return 1, data.decode('hex')

        data = data[0:4] + '81800001000100000000' + data[24:end] + '00010001c00c000100010000003f0004'
        # 十进制表示的IP变为十六进制表示的IP
        # dnsip =  '{:02X}{:02X}{:02X}{:02X}'.format(*map(int, ip.split('.'))).lower()
        dnsIp = ip2Hex(ip)
        data = data + dnsIp
        return 1, hexToByte(data)
    return 0, hexToByte(data)
