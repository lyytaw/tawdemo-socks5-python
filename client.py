#!/usr/bin/env python
# @Time    : 2019-06-01
# @Author  : cayun

import sys
import argparse
import asyncio

import common


class Client:

    def __init__(self, args):
        options = self.parse_args(args)
        self.local_port = options.local_port
        self.remote_host = options.remote_host
        self.remote_port = options.remote_port
        self.password = options.password
        self.loop = asyncio.get_event_loop()

    def parse_args(self, args):
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('-lp', '--local-port', dest='local_port', required=True, help='local listening port')
        arg_parser.add_argument('-rh', '--remote-host', dest='remote_host', required=True, help='remote host')
        arg_parser.add_argument('-rp', '--remote-port', dest='remote_port', required=True, help='remote port')
        arg_parser.add_argument('-P', '--password', dest='password', required=True, help='password')
        return arg_parser.parse_args(args)

    def server_loop(self):
        self.loop.run_until_complete(self.start_listening(self.local_port))
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()

    async def start_listening(self, port):
        await asyncio.start_server(self.transfer_data, 'localhost', port)

    async def transfer_data(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        remote_reader, remote_writer = await asyncio.open_connection(self.remote_host, self.remote_port, loop=self.loop)
        asyncio.run_coroutine_threadsafe(common.transfer_data_with_compress(reader, remote_writer, self.password), self.loop)
        asyncio.run_coroutine_threadsafe(common.transfer_data_with_decompress(remote_reader, writer, self.password), self.loop)

    def start(self):
        self.server_loop()


if __name__ == '__main__':
    client = Client(sys.argv[1:])
    client.start()
