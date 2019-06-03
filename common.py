#!/usr/bin/env python
# @Time    : 2019-06-01
# @Author  : cayun

import asyncio
from constant import *


async def read_data(reader: asyncio.StreamReader, decompress: bool, password: int):
    if decompress:
        data = await reader.read(BUFF_SIZE)
        if not data:
            return data
        data = decrypt_bytes(data, password)
        return data
    else:
        data = await reader.read(BUFF_SIZE)
        return data


def write_data(writer: asyncio.StreamWriter, data: bytes, compress: bool, password: int):
    if compress:
        data = encrypt_bytes(data, password)
        writer.write(data)
    else:
        writer.write(data)


async def transfer_data_with_compress(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, password: int):
    while True:
        data = await read_data(reader, False, password)
        if not data:
            writer.close()
            break
        write_data(writer, data, True, password)
    writer.close()


async def transfer_data_with_decompress(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, password: int):
    while True:
        data = await read_data(reader, True, password)
        if not data:
            writer.close()
            break
        write_data(writer, data, False, password)
    writer.close()


def encrypt_bytes(bstr: bytes, password: int):
    barr = bytearray(bstr)
    for i in range(len(barr)):
        barr[i] = ((barr[i] ^ password) + password) & 255
    return bytes(barr)


def decrypt_bytes(bstr: bytes, password: int):
    barr = bytearray(bstr)
    for i in range(len(barr)):
        barr[i] = ((barr[i] - password) ^ password) & 255
    return bytes(barr)

