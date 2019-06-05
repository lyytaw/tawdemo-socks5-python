#!/usr/bin/env python
# coding=utf-8

# @Time    : 2019-06-05
# @Author  : hongshu

import asyncio
from asyncio import transports
from typing import Optional, Union, Text, Tuple


class UdpRelayHandler(object):

    def __init__(self, config, loop):
        self.config = config
        self.loop = loop

    def start_client(self):
        self.loop.run_until_complete(self._start_up(self.config.local_port))
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()

    def start_server(self):
        self.loop.run_until_complete(self._start_up(self.config.port))
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()

    async def _start_up(self, port: int):
        transport, protocol = await self.loop.create_datagram_endpoint(
            lambda: UdpRelayProtocol(),
            remote_addr=('0.0.0.0', port)
        )


class UdpRelayProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        self.transport = None

    def datagram_received(self, data: Union[bytes, Text], addr: Tuple[str, int]) -> None:
        super().datagram_received(data, addr)

    def error_received(self, exc: Exception) -> None:
        super().error_received(exc)

    def connection_made(self, transport: transports.BaseTransport) -> None:
        self.transport = transport

    def connection_lost(self, exc: Optional[Exception]) -> None:
        super().connection_lost(exc)
