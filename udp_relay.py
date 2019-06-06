#!/usr/bin/env python
# coding=utf-8

# @Time    : 2019-06-05
# @Author  : hongshu

import asyncio
import common


class UdpRelayHandler(object):

    def __init__(self, is_client, config, loop):
        self.is_client = is_client
        self.config = config
        self.loop = loop

    async def start(self):
        await self._listening()

    async def _listening(self):
        if self.is_client:
            transport, protocol = await self.loop.create_datagram_endpoint(
                lambda: UdpRelayReceiverProtocol(True, self.config, self.loop),
                local_addr=('0.0.0.0', self.config.client_port)
            )
        else:
            transport, protocol = await self.loop.create_datagram_endpoint(
                lambda: UdpRelayReceiverProtocol(False, self.config, self.loop),
                local_addr=('0.0.0.0', self.config.server_port)
            )


class UdpRelayReceiverProtocol(asyncio.DatagramProtocol):

    def __init__(self, is_client, config, loop):
        self.transport = None
        self.is_client = is_client
        self.config = config
        self.loop = loop

    def datagram_received(self, data, addr):
        print('receive1:')
        print(data)
        if self.is_client:
            asyncio.wait(asyncio.ensure_future(self._transfer_data(data)), loop=self.loop)
        else:
            asyncio.wait(asyncio.ensure_future(self._transfer_data(data)), loop=self.loop)

    def connection_made(self, transport):
        self.transport = transport

    async def _transfer_data(self, data):
        print('transfer:')
        print(data)
        if self.is_client:
            sender_transport, sender_potocol = await self.loop.create_datagram_endpoint(
                lambda: UdpRelaySenderProtocol(data, self.transport, self.is_client, self.config),
                remote_addr=(self.config.server_host, self.config.server_port)
            )
            data = common.encrypt_bytes(data, self.config.password)
            sender_transport.sendto(data, (self.config.server_host, self.config.server_port))
        else:
            data = common.decrypt_bytes(data, self.config.password)
            frag, dst_host, dst_port, header, data = self._parse_udp_data(data)
            if frag != 0 or not dst_host:
                return
            sender_transport, sender_potocol = await self.loop.create_datagram_endpoint(
                lambda: UdpRelaySenderProtocol(header, self.transport, self.is_client, self.config),
                remote_addr=(dst_host, dst_port)
            )
            sender_transport.sendto(data, (dst_host, dst_port))

    def _parse_udp_data(self, data):
        frag = data[2]
        if data[3] == 0x01:           # IPv4
            host = '%d.%d.%d.%d' % (int(data[4]), int(data[5]), int(data[6]), int(data[7]))
            port = common.get_port_from_bytes(data[8: 10])
            header = data[:10]
            data = data[10:]
        elif data[3] == 0x03:         # domain
            p = 5 + int(data[4])
            host = data[5: p]
            port = common.get_port_from_bytes(data[p: p+2])
            header = data[:7+int(data[4])]
            data = data[7+int(data[4]):]
        else:
            host = None
            port = None
            header = None
            data = None
        return frag, host, port, header, data


class UdpRelaySenderProtocol(asyncio.DatagramProtocol):

    def __init__(self, header, src_transport, is_client, config):
        self.src_transport = src_transport
        self.header = header
        self.transport = None
        self.is_client = is_client
        self.config = config

    def datagram_received(self, data, addr):
        print('receive2:')
        print(data)
        if self.is_client:
            data = common.decrypt_bytes(data, self.config.password)
        else:
            data = self.header + data
            data = common.encrypt_bytes(data, self.config.password)
        self.src_transport.sendto(data)

    def connection_made(self, transport):
        self.transport = transport
