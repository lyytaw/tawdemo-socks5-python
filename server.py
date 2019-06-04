#!/usr/bin/env python
# @Time    : 2019-06-01
# @Author  : cayun

import sys
import argparse
import asyncio

from tcp_relay import TcpRelayHandler


def _parse_args(args):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-p', '--port', dest='port', type=int, required=True, help='listening port')
    arg_parser.add_argument('-h', '--host', dest='host', required=True, help='local host/ip')
    arg_parser.add_argument('-P', '--password', type=int, dest='password', required=True, help='password')
    return arg_parser.parse_args(args)


def main():
    config = _parse_args(sys.argv[1:])
    loop = asyncio.get_event_loop()
    tcp_relay_handler = TcpRelayHandler(config, loop)
    tcp_relay_handler.start_server()


if __name__ == '__main__':
    main()
