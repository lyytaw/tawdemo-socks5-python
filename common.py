#!/usr/bin/env python
# @Time    : 2019-06-01
# @Author  : cayun

import random
import zlib
import asyncio
from constant import *


async def read_data(reader: asyncio.StreamReader, decompress: bool):
    if decompress:
        data = await reader.read(1)
        if not data:
            return data
        rand = int.from_bytes(bytes=data, byteorder='big', signed=True)
        data = await reader.read(2)
        if not data:
            return data
        nxt = int.from_bytes(bytes=data, byteorder='big', signed=True)
        data = await reader.read(nxt)
        data = zlib.decompress(data)
        data = xor_bytes(data, rand)
        return data
    else:
        data = await reader.read(BUFF_SIZE)
        return data


def write_data(writer: asyncio.StreamWriter, data: bytes, compress: bool):
    if compress:
        rand = random.randint(0, 100)
        data = xor_bytes(data, rand)
        data = zlib.compress(data)
        writer.write(rand.to_bytes(length=1, byteorder='big', signed=True))
        writer.write(len(data).to_bytes(length=2, byteorder='big', signed=True))
        writer.write(data)
    else:
        writer.write(data)


async def transfer_data_with_compress(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    while True:
        data = await read_data(reader, False)
        if not data:
            break
        print('read data:')
        print(data)
        write_data(writer, data, True)
    writer.close()


async def transfer_data_with_decompress(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    while True:
        data = await read_data(reader, True)
        if not data:
            break
        print('write data:')
        print(data)
        write_data(writer, data, False)
    writer.close()


def xor_bytes(bstr: bytes, rand: int):
    barr = bytearray(bstr)
    for i in range(len(barr)):
        barr[i] ^= rand
    return bytes(barr)
