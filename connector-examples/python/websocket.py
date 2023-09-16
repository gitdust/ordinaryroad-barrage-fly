#  Copyright 2023 OrdinaryRoad
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import argparse
import asyncio
import json
import logging
from asyncio import Event
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import AsyncGenerator, Tuple

import aiohttp
from reactivestreams.subscriber import Subscriber
from reactivestreams.subscription import Subscription
from rsocket.helpers import single_transport_provider
from rsocket.payload import Payload
from rsocket.rsocket_client import RSocketClient
from rsocket.streams.stream_from_async_generator import StreamFromAsyncGenerator
from rsocket.transports.aiohttp_websocket import TransportAioHttpClient

json_encoder = json.JSONEncoder()

subscribe_payload_json = {
    "data": {
        "taskIds": [],
        "cmd": "SUBSCRIBE"
    },
    "metadata": {}
}


class ChannelSubscriber(Subscriber):
    def __init__(self, wait_for_responder_complete: Event) -> None:
        super().__init__()
        self.subscription = None
        self._wait_for_responder_complete = wait_for_responder_complete

    def on_subscribe(self, subscription: Subscription):
        self.subscription = subscription
        self.subscription.request(0x7FFFFFFF)

    def on_next(self, value: Payload, is_complete=False):
        logging.info('From server on channel: ' + value.data.decode('utf-8'))
        if is_complete:
            self._wait_for_responder_complete.set()

    def on_error(self, exception: Exception):
        logging.error('Error from server on channel' + str(exception))
        self._wait_for_responder_complete.set()

    def on_complete(self):
        logging.info('Completed from server on channel')
        self._wait_for_responder_complete.set()


@asynccontextmanager
async def connect(server_host, server_port):
    """
    创建一个Client，建立连接并return
    """
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('ws://%s:%s' % (server_host, server_port)) as websocket:
            async with RSocketClient(
                    single_transport_provider(TransportAioHttpClient(websocket=websocket)),
                    keep_alive_period=timedelta(seconds=30),
                    max_lifetime_period=timedelta(days=1)
            ) as client:
                yield client


async def main(server_host, server_port):
    # 1 建立连接
    async with connect(server_host, server_port) as client:
        # 阻塞等待Channel关闭事件
        channel_completion_event = Event()

        # ==============================begin==============================#
        #
        #
        #
        #
        #
        # 定义Client向Channel发送消息的Publisher
        # Python没有匿名内部类，这里定义一个方法作为参数，传给StreamFromAsyncGenerator类
        async def generator() -> AsyncGenerator[Tuple[Payload, bool], None]:
            # 2 发送订阅Task的请求
            # Payload：Client通过Channel向Server发送的消息，False表示不需要关闭Channel
            yield Payload(
                data=json_encoder.encode(subscribe_payload_json["data"]).encode(),
                metadata=json_encoder.encode(subscribe_payload_json["metadata"]).encode()
            ), False
            # 发送了一条订阅消息后直接暂停发送即可
            await Event().wait()

        stream = StreamFromAsyncGenerator(generator)
        # ========== end ==========#
        #
        #
        #
        #
        # ============================== end ==============================#

        # ==============================begin==============================#
        #
        #
        #
        #
        # Client请求一个Channel，Payload留空，turn StreamHandler
        requested = client.request_channel(Payload(), stream)
        #
        #
        #
        #
        # ============================== end ==============================#

        # ==============================begin==============================#
        #
        #
        #
        #
        #
        # 3 订阅Channel，ChannelSubscriber用于处理Server通过Channel回复的消息
        requested.subscribe(ChannelSubscriber(channel_completion_event))
        #
        #
        #
        #
        #
        # ============================== end ==============================#
        await channel_completion_event.wait()


if __name__ == '__main__':
    """
    参考：https://github.com/rsocket/rsocket-py
    > First Run
    pip3 install rsocket
    pip3 install aiohttp
    
    python websocket.py $PORT
    """
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost', type=str, help="HOST")
    parser.add_argument('-p', default='9898', type=int, help="PORT")
    parser.add_argument('-t', action='append', required=True, help="taskIds")
    args = parser.parse_args()

    host = args.host
    port = args.p
    subscribe_payload_json["data"]["taskIds"] = args.t
    print(subscribe_payload_json)
    asyncio.run(main(host, port))