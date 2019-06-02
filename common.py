#!/usr/bin/env python
# @Time    : 2019-06-01
# @Author  : cayun

import zlib
import asyncio


async def read_data(reader: asyncio.StreamReader, decompress: bool):
    if decompress:
        data = await reader.read(2)
        if not data:
            return data
        nxt = int.from_bytes(bytes=data, byteorder='big', signed=True)
        data = await reader.read(nxt)
        data = zlib.decompress(data)
        return data
    else:
        data = await reader.read(8196)
        return data


def write_data(writer: asyncio.StreamWriter, data: bytes, compress: bool):
    if compress:
        data = zlib.compress(data)
        writer.write(len(data).to_bytes(length=2, byteorder='big', signed=True))
        writer.write(data)
    else:
        writer.write(data)


async def transfer_data_with_compress(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    while True:
        data = await read_data(reader, False)
        if not data:
            break
        write_data(writer, data, True)
    writer.close()


async def transfer_data_with_decompress(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    while True:
        data = await read_data(reader, True)
        if not data:
            break
        write_data(writer, data, False)
    writer.close()
