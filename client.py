#!/usr/bin/env python
# @Time    : 2019-06-01
# @Author  : cayun

import sys
import argparse
import asyncio

from tcp_relay import TcpRelayHandler


def _parse_args(args):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-lp', '--local-port', dest='local_port', required=True, help='local listening port')
    arg_parser.add_argument('-rh', '--remote-host', dest='remote_host', required=True, help='remote host')
    arg_parser.add_argument('-rp', '--remote-port', dest='remote_port', required=True, help='remote port')
    arg_parser.add_argument('-P', '--password', type=int, dest='password', required=True, help='password')
    return arg_parser.parse_args(args)


def main():
    config = _parse_args(sys.argv[1:])
    loop = asyncio.get_event_loop()
    tcp_relay_handler = TcpRelayHandler(config, loop)
    tcp_relay_handler.start_client()


if __name__ == '__main__':
    main()
