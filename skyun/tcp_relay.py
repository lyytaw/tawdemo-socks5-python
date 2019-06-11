#!/usr/bin/env python
# coding=utf-8

# @Time    : 2019-06-04
# @Author  : hongshu

import sys
import asyncio

from skyun import common


class TcpRelayHandler(object):

    def __init__(self, is_client, config, loop):
        self.is_client = is_client
        self.config = config
        self.loop = loop

    async def start(self):
        await self._listening()

    async def _listening(self):
        if self.is_client:
            await asyncio.start_server(self._shake_hand, '0.0.0.0', self.config.client_port, loop=self.loop)
        else:
            await asyncio.start_server(self._establish_connection, '0.0.0.0', self.config.server_port, loop=self.loop)

    async def _shake_hand(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = await common.read_data(reader, False, self.config.password)
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
        common.write_data(writer, b'\x05\x00', False, self.config.password)

    def _shake_hand_fail(self, writer):
        common.write_data(writer, b'\x05\xff', False, self.config.password)

    async def _establish_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        if self.is_client:
            data = await common.read_data(reader, False, self.config.password)
            try:
                remote_reader, remote_writer = \
                    await asyncio.open_connection(self.config.server_host, self.config.server_port, loop=self.loop)
            except:
                print('connot connect to proxy server')
                self._establish_connection_fail(writer, 0x04)
                writer.close()
                return
            common.write_data(remote_writer, data, True, self.config.password)
            data = await common.read_data(remote_reader, True, self.config.password)
            if data[1] == 0x00:
                self._establish_connection_success(writer)
            else:
                self._establish_connection_fail(writer, data[1])
                writer.close()
                return
            await self._transfer_data(reader, writer, remote_reader, remote_writer)
        else:
            data = await common.read_data(reader, True, self.config.password)
            if data[0] != 0x05 or data[2] != 0x00:
                self._establish_connection_fail(writer, 0x02)
                writer.close()
                return

            # 只支持TCP和UDP
            if data[1] == 0x01:    # TCP
                pass
            elif data[1] == 0x03:    # UDP
                self._establish_connection_success(writer)
                return
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
            await self._transfer_data(reader, writer, remote_reader, remote_writer)

    def _establish_connection_success(self, writer):
        if self.is_client:
            data = bytes([0x05, 0x00, 0x00, 0x01, 0, 0, 0, 0])
            data += common.convert_port_to_bytes(self.config.client_port)
            common.write_data(writer, data, False, self.config.password)
        else:
            data = bytes([0x05, 0x00])
            common.write_data(writer, data, True, self.config.password)

    def _establish_connection_fail(self, writer, error_code):
        if self.is_client:
            data = bytes([0x05, error_code, 0x00, 0x01, 0, 0, 0, 0])
            data += common.convert_port_to_bytes(self.config.client_port)
            common.write_data(writer, data, False, self.config.password)
        else:
            data = bytes([0x05, error_code])
            common.write_data(writer, data, True, self.config.password)

    async def _transfer_data(self, reader, writer, remote_reader, remote_writer):
        if self.is_client:
            await asyncio.gather(
                common.transfer_data_with_encrypt(reader, remote_writer, self.config.password),
                common.transfer_data_with_decrypt(remote_reader, writer, self.config.password),
                loop=self.loop
            )
        else:
            await asyncio.gather(
                common.transfer_data_with_decrypt(reader, remote_writer, self.config.password),
                common.transfer_data_with_encrypt(remote_reader, writer, self.config.password),
                loop=self.loop
            )
