#!/usr/bin/env python
# @Time    : 2019-06-01
# @Author  : cayun

import sys
import argparse
import asyncio

from tawsocks.tcp_relay import TcpRelayHandler
from tawsocks.udp_relay import UdpRelayHandler


def _parse_args(args):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-lp', '--local-port', dest='client_port', type=int,
                            required=True, help='本地监听端口')
    arg_parser.add_argument('-rh', '--remote-host', dest='server_host', required=True, help='服务器地址')
    arg_parser.add_argument('-rp', '--remote-port', dest='server_port', type=int, required=True, help='服务器端口')
    arg_parser.add_argument('-P', '--password', dest='password', required=True, help='密码')
    return arg_parser.parse_args(args)


def main():
    config = _parse_args(sys.argv[1:])
    loop = asyncio.get_event_loop()
    tcp_relay_handler = TcpRelayHandler(True, config, loop)
    udp_relay_handler = UdpRelayHandler(True, config, loop)

    tasks = [
        asyncio.ensure_future(tcp_relay_handler.start()),
        asyncio.ensure_future(udp_relay_handler.start())
    ]

    loop.run_until_complete(asyncio.wait(tasks))
    try:
        loop.run_forever()
    finally:
        loop.close()


if __name__ == '__main__':
    main()
