#!/usr/bin/env python
# coding=utf-8

# @Time    : 2019-06-05
# @Author  : hongshu

import struct
import asyncio

from skyun import common


class UdpRelayHandler(object):

    def __init__(self, is_client, config, loop):
        self.is_client = is_client
        self.config = config
        self.loop = loop

    async def start(self):
        await self._listening()

    async def _listening(self):
        if self.is_client:
            await self.loop.create_datagram_endpoint(
                lambda: UdpRelayProtocol(self.is_client, self.config, self.loop),
                local_addr=('0.0.0.0', self.config.client_port)
            )
        else:
            await self.loop.create_datagram_endpoint(
                lambda: UdpRelayProtocol(self.is_client, self.config, self.loop),
                local_addr=('0.0.0.0', self.config.server_port)
            )


class UdpRelayProtocol(asyncio.DatagramProtocol):

    def __init__(self, is_client, config, loop):
        self.transport = None
        self.is_client = is_client
        self.config = config
        self.loop = loop
        self.dst_src_dict = {}
        self.header_cache = {}

    def datagram_received(self, data, addr):
        if self.is_client:
            if addr == (self.config.server_host, self.config.server_port):   # 来自服务端
                data = common.decrypt_bytes(data, self.config.password)
                host, port, data = self._parse_custom_data(data)
                data = self.header_cache[(host, port)] + data
                self.transport.sendto(data, self.dst_src_dict[(host, port)])
            else:    # 来自用户
                frag, host, port, header, data = self._parse_socks_data(data)
                if frag != 0 or not host:
                    return
                self.dst_src_dict[(host, port)] = addr
                data = self._wrap_custom_data(host, port, data)
                data = common.encrypt_bytes(data, self.config.password)
                self.header_cache[(host, port)] = header
                self.transport.sendto(data, (self.config.server_host, self.config.server_port))
        else:
            if addr not in self.dst_src_dict:    # 来自客户端
                data = common.decrypt_bytes(data, self.config.password)
                host, port, data = self._parse_custom_data(data)
                self.dst_src_dict[(host, port)] = addr
                self.transport.sendto(data, (host, port))
            else:    # 来自远端
                data = self._wrap_custom_data(addr[0], addr[1], data)
                data = common.encrypt_bytes(data, self.config.password)
                self.transport.sendto(data, self.dst_src_dict[(addr[0], addr[1])])

    def connection_made(self, transport):
        self.transport = transport

    def _parse_socks_data(self, data: bytes) -> (int, str, int, bytes, bytes):
        frag = data[2]
        if data[3] == 0x01:  # IPv4
            host = '%d.%d.%d.%d' % (int(data[4]), int(data[5]), int(data[6]), int(data[7]))
            port = common.get_port_from_bytes(data[8: 10])
            header = data[:10]
            data = data[10:]
        elif data[3] == 0x03:  # domain
            p = 5 + int(data[4])
            host = str(data[5: p], encoding='utf-8')
            port = common.get_port_from_bytes(data[p: p + 2])
            header = data[:7 + int(data[4])]
            data = data[7 + int(data[4]):]
        else:
            host = None
            port = None
            header = None
            data = None
        return frag, host, port, header, data

    def _parse_custom_data(self, data: bytes) -> (str, int, bytes):
        nxt_len = struct.unpack('B', data[0:1])[0]
        host = str(data[1: 1+nxt_len], encoding='utf-8')
        port = struct.unpack('>H', data[1+nxt_len: 3+nxt_len])[0]
        data = data[3+nxt_len:]
        return host, port, data

    def _wrap_custom_data(self, host: str, port: int, data: bytes) -> bytes:
        result = struct.pack('B', len(host))
        result += bytes(host, encoding='utf-8')
        result += struct.pack('>H', port)
        result += data
        return result
