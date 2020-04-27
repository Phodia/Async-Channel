#  Drakkar-Software OctoBot-Channels
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.

import pytest

from octobot_channels.channels.channel import Channel, del_chan, get_chan, set_chan
from octobot_channels.channels.channel_instances import ChannelInstances
from octobot_channels.constants import CHANNEL_WILDCARD
from octobot_channels.util.channel_creator import create_channel_instance

from tests import TEST_CHANNEL, EMPTY_TEST_CHANNEL, EmptyTestChannel, empty_test_callback, EmptyTestProducer


@pytest.yield_fixture()
async def test_channel():
    del_chan(EMPTY_TEST_CHANNEL)
    yield await create_channel_instance(EmptyTestChannel, set_chan)
    await get_chan(TEST_CHANNEL).stop()


@pytest.mark.asyncio
async def test_get_chan():
    class TestChannel(Channel):
        pass

    del_chan(TEST_CHANNEL)
    await create_channel_instance(TestChannel, set_chan)
    await get_chan(TEST_CHANNEL).stop()


@pytest.mark.asyncio
async def test_set_chan():
    class TestChannel(Channel):
        pass

    del_chan(TEST_CHANNEL)
    await create_channel_instance(TestChannel, set_chan)
    with pytest.raises(ValueError):
        set_chan(TestChannel(), name=TestChannel.get_name())
    await get_chan(TEST_CHANNEL).stop()


@pytest.mark.asyncio
async def test_set_chan_using_default_name():
    class TestChannel(Channel):
        pass

    del_chan(TEST_CHANNEL)
    channel = TestChannel()
    returned_channel = set_chan(channel, name=None)
    assert returned_channel is channel
    assert channel.get_name() is not None
    assert ChannelInstances.instance().channels[channel.get_name()] == channel
    with pytest.raises(ValueError):
        set_chan(TestChannel(), name=TestChannel.get_name())
    await get_chan(TEST_CHANNEL).stop()


@pytest.mark.asyncio
async def test_get_internal_producer():
    class TestChannel(Channel):
        pass

    del_chan(TEST_CHANNEL)
    await create_channel_instance(TestChannel, set_chan)
    with pytest.raises(TypeError):
        get_chan(TEST_CHANNEL).get_internal_producer()
    await get_chan(TEST_CHANNEL).stop()


@pytest.mark.asyncio
async def test_new_consumer_without_producer(test_channel):
    await get_chan(EMPTY_TEST_CHANNEL).new_consumer(empty_test_callback)
    assert len(get_chan(EMPTY_TEST_CHANNEL).consumers) == 1


@pytest.mark.asyncio
async def test_new_consumer_without_filters(test_channel):
    consumer = await get_chan(EMPTY_TEST_CHANNEL).new_consumer(empty_test_callback)
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumers() == [consumer]


@pytest.mark.asyncio
async def test_new_consumer_with_filters(test_channel):
    consumer = await get_chan(EMPTY_TEST_CHANNEL).new_consumer(empty_test_callback, {"test_key": 1})
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumers() == [consumer]
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({}) == [consumer]  # returns all if empty
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({"test_key": 2}) == []
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({"test_key": 1, "test2": 2}) == []
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({"test_key": 1}) == [consumer]


@pytest.mark.asyncio
async def test_new_consumer_with_expected_wildcard_filters(test_channel):
    consumer = await get_chan(EMPTY_TEST_CHANNEL).new_consumer(empty_test_callback, {"test_key": 1,
                                                                                     "test_key_2": "abc"})
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumers() == [consumer]
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({}) == [consumer]  # returns all if empty
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({"test_key": 1, "test_key_2": "abc"}) == [consumer]
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters(
        {"test_key": 1, "test_key_2": "abc", "test_key_3": 45}) == []
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters(
        {"test_key": 1, "test_key_2": "abc", "test_key_3": CHANNEL_WILDCARD}) == [consumer]
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({"test_key": 4, "test_key_2": "bc"}) == []
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({"test_key": 1, "test_key_2": CHANNEL_WILDCARD}) == [
        consumer]
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({"test_key": 3, "test_key_2": CHANNEL_WILDCARD}) == []
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters(
        {"test_key": CHANNEL_WILDCARD, "test_key_2": "abc"}) == [consumer]
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters(
        {"test_key": CHANNEL_WILDCARD, "test_key_2": "a"}) == []
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters(
        {"test_key": CHANNEL_WILDCARD, "test_key_2": CHANNEL_WILDCARD}) == [consumer]


@pytest.mark.asyncio
async def test_new_consumer_with_consumer_wildcard_filters(test_channel):
    consumer = await get_chan(EMPTY_TEST_CHANNEL).new_consumer(empty_test_callback, {"test_key": 1,
                                                                                     "test_key_2": "abc",
                                                                                     "test_key_3": CHANNEL_WILDCARD})
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumers() == [consumer]
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({}) == [consumer]  # returns all if empty
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({"test_key": 1, "test_key_2": "abc"}) == [consumer]
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters(
        {"test_key": 1, "test_key_2": "abc", "test_key_3": 45}) == [consumer]
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters(
        {"test_key": 1, "test_key_2": "abc", "test_key_3": CHANNEL_WILDCARD}) == [consumer]
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({"test_key": 4, "test_key_2": "bc"}) == []
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({"test_key": 1, "test_key_2": CHANNEL_WILDCARD}) == [
        consumer]
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({"test_key": 1}) == [consumer]
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({"test_key_2": CHANNEL_WILDCARD}) == [consumer]
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({"test_key_3": CHANNEL_WILDCARD}) == [consumer]
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({"test_key_3": "e"}) == [consumer]
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({"test_key": 3, "test_key_2": CHANNEL_WILDCARD}) == []
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters(
        {"test_key": CHANNEL_WILDCARD, "test_key_2": "abc"}) == [consumer]
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters(
        {"test_key": CHANNEL_WILDCARD, "test_key_2": "a"}) == []
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters(
        {"test_key": CHANNEL_WILDCARD, "test_key_2": "a", "test_key_3": CHANNEL_WILDCARD}) == []
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters(
        {"test_key": CHANNEL_WILDCARD, "test_key_2": CHANNEL_WILDCARD}) == [consumer]


@pytest.mark.asyncio
async def test_new_consumer_with_multiple_consumer_filtering(test_channel):
    consumers_descriptions = [
        {"A": 1, "B": 2, "C": CHANNEL_WILDCARD},  # 0
        {"A": False, "B": "BBBB", "C": CHANNEL_WILDCARD},  # 1
        {"A": 3, "B": CHANNEL_WILDCARD, "C": CHANNEL_WILDCARD},  # 2
        {"A": CHANNEL_WILDCARD, "B": CHANNEL_WILDCARD, "C": CHANNEL_WILDCARD},  # 3
        {"A": CHANNEL_WILDCARD, "B": 2, "C": 1},  # 4
        {"A": True, "B": CHANNEL_WILDCARD, "C": CHANNEL_WILDCARD},  # 5
        {"A": None, "B": None, "C": CHANNEL_WILDCARD},  # 6
        {"A": "PPP", "B": 1, "C": CHANNEL_WILDCARD, "D": 5},  # 7
        {"A": CHANNEL_WILDCARD, "B": 2, "C": "ABC"},  # 8
        {"A": CHANNEL_WILDCARD, "B": True, "C": CHANNEL_WILDCARD},  # 9
        {"A": CHANNEL_WILDCARD, "B": 6, "C": CHANNEL_WILDCARD, "D": CHANNEL_WILDCARD},  # 10
        {"A": CHANNEL_WILDCARD, "B": CHANNEL_WILDCARD, "C": CHANNEL_WILDCARD, "D": CHANNEL_WILDCARD},  # 11
        {"A": None, "B": False, "C": "LLLL", "D": CHANNEL_WILDCARD},  # 12
        {"A": None, "B": None, "C": CHANNEL_WILDCARD, "D": None},  # 13
        {"A": CHANNEL_WILDCARD, "B": 2, "C": CHANNEL_WILDCARD, "D": None},  # 14
        {"A": CHANNEL_WILDCARD, "B": [2, 3, 4, 5, 6], "C": CHANNEL_WILDCARD, "D": None},  # 15
        {"A": CHANNEL_WILDCARD, "B": ["A", 5, "G"], "C": CHANNEL_WILDCARD, "D": None},  # 16
        {"A": [1, 2, 3], "B": 2, "C": CHANNEL_WILDCARD, "D": CHANNEL_WILDCARD},  # 17
        {"A": ["A", "B", "C"], "B": 2, "C": CHANNEL_WILDCARD, "D": CHANNEL_WILDCARD},  # 18
        {"A": CHANNEL_WILDCARD, "B": [2], "C": CHANNEL_WILDCARD, "D": CHANNEL_WILDCARD},  # 19
        {"A": CHANNEL_WILDCARD, "B": ["B"], "C": CHANNEL_WILDCARD, "D": CHANNEL_WILDCARD},  # 20
        {"A": 18, "B": ["A", "B", "C"], "C": ["---", "9", "#"], "D": CHANNEL_WILDCARD},  # 21
        {"A": [9, 18], "B": ["B", "C", "D"], "C": ["---", "9", "#", "@", "{"], "D": ["P", "__str__"]}  # 22
    ]

    consumers = [
        await get_chan(EMPTY_TEST_CHANNEL).new_consumer(empty_test_callback, consumers_description)
        for consumers_description in consumers_descriptions
    ]

    assert get_chan(EMPTY_TEST_CHANNEL).get_consumers() == consumers
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({}) == consumers
    # Warning : consumer[5] is returned because 1 == True
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({"A": 1, "B": "6"}) == \
           [consumers[3], consumers[5], consumers[11]]
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({"A": CHANNEL_WILDCARD, "B": "G", "C": "1A"}) == \
           [consumers[2], consumers[3], consumers[5], consumers[11], consumers[16]]
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({"A": CHANNEL_WILDCARD, "B": CHANNEL_WILDCARD,
                                                                   "C": CHANNEL_WILDCARD}) == consumers
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({"A": 18, "B": "A", "C": "#"}) == \
           [consumers[3], consumers[11], consumers[16], consumers[21]]
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({"A": 18, "B": "C", "C": "#", "D": None}) == \
           [consumers[11], consumers[21]]
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({"A": 18, "B": "C", "C": "^", "D": None}) == \
           [consumers[11]]
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumer_from_filters({"A": 18, "B": "C", "C": "#", "D": "__str__"}) == \
           [consumers[11], consumers[21], consumers[22]]


@pytest.mark.asyncio
async def test_remove_consumer(test_channel):
    consumer = await get_chan(EMPTY_TEST_CHANNEL).new_consumer(empty_test_callback)
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumers() == [consumer]
    await get_chan(EMPTY_TEST_CHANNEL).remove_consumer(consumer)
    assert get_chan(EMPTY_TEST_CHANNEL).get_consumers() == []


@pytest.mark.asyncio
async def test_unregister_producer(test_channel):
    assert get_chan(EMPTY_TEST_CHANNEL).producers == []
    producer = EmptyTestProducer(None)
    await get_chan(EMPTY_TEST_CHANNEL).register_producer(producer)
    assert get_chan(EMPTY_TEST_CHANNEL).producers == [producer]


@pytest.mark.asyncio
async def test_register_producer(test_channel):
    assert get_chan(EMPTY_TEST_CHANNEL).producers == []
    producer = EmptyTestProducer(None)
    await get_chan(EMPTY_TEST_CHANNEL).register_producer(producer)
    assert get_chan(EMPTY_TEST_CHANNEL).producers == [producer]
    get_chan(EMPTY_TEST_CHANNEL).unregister_producer(producer)
    assert get_chan(EMPTY_TEST_CHANNEL).producers == []


@pytest.mark.asyncio
async def test_flush(test_channel):
    producer = EmptyTestProducer(test_channel)
    await test_channel.register_producer(producer)
    producer2 = EmptyTestProducer(test_channel)
    await test_channel.register_producer(producer2)
    producer3 = EmptyTestProducer(test_channel)
    test_channel.internal_producer = producer3

    assert producer3.channel is test_channel
    for producer in test_channel.producers:
        assert producer.channel is test_channel

    test_channel.flush()
    assert test_channel.internal_producer.channel is None
    for producer in test_channel.producers:
        assert producer.channel is None
