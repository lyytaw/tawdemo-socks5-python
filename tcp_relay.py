#!/usr/bin/env python
# coding=utf-8

# @Time    : 2019-06-04
# @Author  : hongshu

import sys
import asyncio

import common


class TcpRelayHandler(object):

    def __init__(self, config, loop):
        self.config = config
        self.loop = loop

    def start_client(self):
        asyncio.run_coroutine_threadsafe(self._listening(self.config.local_port, self._transfer_data), self.loop)
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()

    def start_server(self):
        asyncio.run_coroutine_threadsafe(self._listening(self.config.port, self._shake_hand), self.loop)
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()

    async def _listening(self, port: int, connect_callback):
        await asyncio.start_server(connect_callback, '0.0.0.0', port, loop=self.loop)

    async def _transfer_data(self, reader, writer):
        remote_reader, remote_writer = \
            await asyncio.open_connection(self.config.remote_host, self.config.remote_port, loop=self.loop)
        asyncio.run_coroutine_threadsafe(
            common.transfer_data_with_compress(reader, remote_writer, self.config.password), self.loop)
        asyncio.run_coroutine_threadsafe(
            common.transfer_data_with_decompress(remote_reader, writer, self.config.password), self.loop)

    async def _shake_hand(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = await common.read_data(reader, True, self.config.password)
        if len(data) < 2 or len(data) != 2 + data[1] or data[0] != 0x05:
            self._shake_hand_fail(writer)
            writer.close()
            return

        # 判断客户端是否接受"无需认证"的方式
        if 0x00 not in data[2:]:
            self._shake_hand_fail(writer)
            writer.close()
            return

        self._shake_hand_success(writer)
        await self._establish_connection(reader, writer)

    def _shake_hand_success(self, writer):
        common.write_data(writer, b'\x05\x00', True, self.config.password)

    def _shake_hand_fail(self, writer):
        common.write_data(writer, b'\x05\xff', True, self.config.password)

    async def _establish_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = await common.read_data(reader, True, self.config.password)
        if data[0] != 0x05 or data[2] != 0x00:
            self._establish_connection_fail(writer, 0x02)
            writer.close()
            return

        if data[1] == 0x01:     # TCP
            self._establish_connection_success(writer)
        elif data[1] == 0x03:   # UDP
            self._establish_connection_success(writer)
        else:
            self._establish_connection_fail(writer, 0x07)
            writer.close()
            return

        if data[3] == 0x01:     # IPv4
            remote_host = '%d.%d.%d.%d' % (int(data[4]), int(data[5]), int(data[6]), int(data[7]))
        elif data[3] == 0x03:   # 域名
            remote_host = str(data[5: -2], encoding='utf-8')
        elif data[3] == 0x04:   # IPv6
            self._establish_connection_fail(writer, 0x08)
            writer.close()
            return
        else:
            self._establish_connection_fail(writer, 0x02)
            writer.close()
            return

        remote_port = int.from_bytes(bytes=data[-2:], byteorder='big')
        print("remote host: %s:%s" % (remote_host, remote_port))

        try:
            remote_reader, remote_writer = await asyncio.open_connection(remote_host, remote_port, loop=self.loop)
        except:
            print('connect fail to %s' % remote_host, file=sys.stderr)
            self._establish_connection_fail(writer, 0x04)
            writer.close()
            return
        self._establish_connection_success(writer)
        asyncio.run_coroutine_threadsafe(
            common.transfer_data_with_decompress(reader, remote_writer, self.config.password), self.loop)
        asyncio.run_coroutine_threadsafe(
            common.transfer_data_with_compress(remote_reader, writer, self.config.password), self.loop)

    def _establish_connection_success(self, writer):
        data = bytes([0x05, 0x00, 0x00, 0x03])
        host = bytes(self.config.host, encoding='utf-8')
        data += len(host).to_bytes(length=1, byteorder='big') + host
        data += common.convert_port_to_bytes(self.config.port)
        common.write_data(writer, data, True, self.config.password)

    def _establish_connection_fail(self, writer, error_code):
        data = bytes([0x05, error_code, 0x00, 0x03])
        host = bytes(self.config.host, encoding='utf-8')
        data += len(host).to_bytes(length=1, byteorder='big') + host
        data += common.convert_port_to_bytes(self.config.port)
        common.write_data(writer, data, True, self.config.password)



