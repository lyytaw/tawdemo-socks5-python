#!/usr/bin/env python
# @Time    : 2019-06-01
# @Author  : cayun

import sys
import argparse
import asyncio

import common


class Server:

    def __init__(self, args):
        options = self.parse_args(args)
        self.port = options.port
        self.loop = asyncio.get_event_loop()

    def parse_args(self, args):
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('-p', '--port', dest='port', required=True, help='listening port')
        return arg_parser.parse_args(args)

    def server_loop(self):
        self.loop.run_until_complete(self.start_listening())
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()

    async def start_listening(self):
        await asyncio.start_server(self.auth_receiver, '0.0.0.0', self.port)

    async def auth_receiver(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = await common.read_data(reader, True)
        if len(data) < 2 or len(data) != 2 + data[1] or data[0] != 0x05:
            self.auth_reply(writer, False)
            return

        # 判断客户端是否接受"无需认证"的方式
        if 0x00 not in data[2:]:
            self.auth_reply(writer, False)
            return

        self.auth_reply(writer, True)
        await self.shake_hand_receiver(reader, writer)

    def auth_reply(self, writer: asyncio.StreamWriter, success: bool):
        data = bytes([0x05, 0x00]) if success else bytes([0x05, 0xFF])
        common.write_data(writer, data, True)

    async def shake_hand_receiver(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = await common.read_data(reader, True)
        if data[0] != 0x05:
            self.shake_hand_reply_fail(writer, 0x02)
            return
        if data[1] != 0x01:
            self.shake_hand_reply_fail(writer, 0x07)
            return
        if data[2] != 0x00:
            self.shake_hand_reply_fail(writer, 0x02)
            return

        remote_host = ''
        if data[3] == 0x01:
            remote_host = data[4: 8].join('.')
        elif data[3] == 0x03:
            remote_host = str(data[5: -2], encoding='utf-8')
        elif data[3] == 0x04:
            self.shake_hand_reply_fail(writer, 0x08)
        else:
            self.shake_hand_reply_fail(writer, 0x02)
            return

        remote_port = int.from_bytes(bytes=data[-2:], byteorder='big')
        print("remote host: %s:%s" % (remote_host, remote_port))

        remote_reader, remote_writer = await asyncio.open_connection(remote_host, remote_port, loop=self.loop)
        self.shake_hand_reply_success(writer)
        asyncio.run_coroutine_threadsafe(common.transfer_data_with_decompress(reader, remote_writer), self.loop)
        asyncio.run_coroutine_threadsafe(common.transfer_data_with_compress(remote_reader, writer), self.loop)

    def shake_hand_reply_success(self, writer):
        data = bytes([0x05, 0x00, 0x00, 0x01, 127, 0, 0, 1, 80, 0])
        common.write_data(writer, data, True)

    def shake_hand_reply_fail(self, writer, error_code):
        data = bytes([0x05, error_code, 0x00, 0x01, 127, 0, 0, 1, 80, 0])
        common.write_data(writer, data, True)

    def start(self):
        self.server_loop()


if __name__ == '__main__':
    server = Server(sys.argv[1:])
    server.start()
