#!/usr/bin/env python
# @Time    : 2019-06-01
# @Author  : cayun

import asyncio
from constant import *


async def read_data(reader: asyncio.StreamReader, decrypt: bool, password: int):
    print('read data:')
    if decrypt:
        data = await reader.read(BUFF_SIZE)
        if not data:
            return data
        data = decrypt_bytes(data, password)
        print(data)
        return data
    else:
        data = await reader.read(BUFF_SIZE)
        print(data)
        return data


def write_data(writer: asyncio.StreamWriter, data: bytes, encrypt: bool, password: int):
    print('write data:')
    print(data)
    if encrypt:
        data = encrypt_bytes(data, password)
        writer.write(data)
    else:
        writer.write(data)


async def transfer_data_with_encrypt(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, password: int):
    while True:
        data = await read_data(reader, False, password)
        if not data:
            writer.close()
            break
        write_data(writer, data, True, password)
    writer.close()


async def transfer_data_with_decrypt(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, password: int):
    while True:
        data = await read_data(reader, True, password)
        if not data:
            writer.close()
            break
        write_data(writer, data, False, password)
    writer.close()


def encrypt_bytes(data: bytes, password: int):
    data = bytearray(data)
    for i in range(len(data)):
        data[i] = ((data[i] ^ password) + password) & 255
    return bytes(data)


def decrypt_bytes(data: bytes, password: int):
    data = bytearray(data)
    for i in range(len(data)):
        data[i] = ((data[i] - password) ^ password) & 255
    return bytes(data)


def get_port_from_bytes(data: bytes):
    return int.from_bytes(bytes=data, byteorder='big')


def convert_port_to_bytes(port: int):
    return port.to_bytes(length=2, byteorder='big')
