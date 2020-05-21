import asyncio
from argparse import ArgumentParser


BUF_SIZE = 16384


def patchcord():
    ap = ArgumentParser()
    ap.add_argument('address1', type=str)
    ap.add_argument('port1', type=int)
    ap.add_argument('address2', type=str)
    ap.add_argument('port2', type=int)
    args = ap.parse_args()
    asyncio.run(do_patchcord(args.address1, args.port1, args.address2, args.port2))


def echo_server():
    ap = ArgumentParser()
    ap.add_argument('address1', type=str)
    ap.add_argument('port1', type=int)
    ap.add_argument('address2', type=str)
    ap.add_argument('port2', type=int)
    args = ap.parse_args()
    asyncio.run(do_echo_server(args.address1, args.port1, args.address2, args.port2))


def tcp_forward():
    ap = ArgumentParser()
    ap.add_argument('listen_address', type=str)
    ap.add_argument('listen_port', type=int)
    ap.add_argument('connect_address', type=str)
    ap.add_argument('connect_port', type=int)
    args = ap.parse_args()
    asyncio.run(do_tcp_forward(args.listen_address, args.listen_port, args.connect_address, args.connect_port))


async def do_patchcord(addr1, port1, addr2, port2):
    peer1 = await asyncio.open_connection(addr1, port1)
    peer2 = await asyncio.open_connection(addr2, port2)
    await pipe(peer1, peer2)


async def do_tcp_forward(listen_address, listen_port, connect_address, connect_port):
    async def on_connect(reader, writer):
        peer1 = reader, writer
        peer2 = await asyncio.open_connection(connect_address, connect_port)
        await pipe(peer1, peer2)
    srv = await asyncio.start_server(on_connect, listen_address, listen_port)
    async with srv:
        await srv.serve_forever()


# TODO: Does not work as expected
async def do_echo_server(addr1, port1, addr2, port2):
    async def on_connect1(reader1, writer1):
        peer1 = reader1, writer1
        async def on_connect2(reader2, writer2):
            peer2 = reader2, writer2
            await pipe(peer1, peer2)

        srv2 = await asyncio.start_server(on_connect2, addr2, port2)
        async with srv2:
            await srv2.serve_forever()

    srv1 = await asyncio.start_server(on_connect1, addr1, port1)
    async with srv1:
        await srv1.serve_forever()


async def relay(reader, writer):
    while True:
        data = await reader.read(BUF_SIZE)
        if not data:
            print('Stream closed')
            return
        writer.write(data)
        await writer.drain()


async def pipe(peer1, peer2):
    r1, w1 = peer1
    r2, w2 = peer2
    await asyncio.gather(relay(r1, w2), relay(r2, w1))
