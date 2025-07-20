# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# Copyright © 2025 aphex5
import asyncio
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import signal
import time
import typing
import bittensor as bt

import core
from core.base.miner import BaseMinerNeuron


class Miner(BaseMinerNeuron):

    def __init__(self, config=None):
        super(Miner, self).__init__(config=config)

        bt.logging.info(f"Attaching forward function to miner axon.")
        self.axon.attach(
            forward_fn=self.pattern_query,
            blacklist_fn=self.blacklist_pattern_query,
            priority_fn=self.priority_pattern_query
        )

        self.axon.attach(
            forward_fn=self.pattern_query_ack,
            blacklist_fn=self._blacklist,
            priority_fn=self.priority_pattern_query_ack,
        )

        bt.logging.info(f"Axon created: {self.axon}")

    async def pattern_query(
        self, synapse: core.protocol.PatternQuery
    ) -> core.protocol.PatternQuery:
       # PLACEHOLDER: PUT YOUR PATTERN DETECTION CODE HERE
       # READ PATTERN FROM DATABASE, SEND TO VALIDATOR
        return synapse

    async def pattern_query_ack(self, synapse: core.protocol.PatternQueryAck) -> core.protocol.PatternQueryAck:
        return synapse

    async def blacklist_pattern_query(self, synapse: core.protocol.PatternQuery) -> typing.Tuple[bool, str]:
         return await self.blacklist_pattern_query(synapse)

    async def blacklist_pattern_query_ack(self, synapse: core.protocol.PatternQueryAck) -> typing.Tuple[bool, str]:
         return await self.blacklist_pattern_query_ack(synapse)

    async def _blacklist(self, synapse: core.protocol.PatternQuery | core.protocol.PatternQueryAck) -> typing.Tuple[bool, str]:

        if synapse.dendrite is None or synapse.dendrite.hotkey is None:
            bt.logging.warning(
                "Received a request without a dendrite or hotkey."
            )
            return True, "Missing dendrite or hotkey"

        uid = self.metagraph.hotkeys.index(synapse.dendrite.hotkey)
        if (
            not self.config.blacklist.allow_non_registered
            and synapse.dendrite.hotkey not in self.metagraph.hotkeys
        ):
            # Ignore requests from un-registered entities.
            bt.logging.trace(
                f"Blacklisting un-registered hotkey {synapse.dendrite.hotkey}"
            )
            return True, "Unrecognized hotkey"

        if self.config.blacklist.force_validator_permit:
            # If the config is set to force validator permit, then we should only allow requests from validators.
            if not self.metagraph.validator_permit[uid]:
                bt.logging.warning(
                    f"Blacklisting a request from non-validator hotkey {synapse.dendrite.hotkey}"
                )
                return True, "Non-validator hotkey"

        bt.logging.trace(
            f"Not Blacklisting recognized hotkey {synapse.dendrite.hotkey}"
        )
        return False, "Hotkey recognized!"

    async def priority_pattern_query_ack(self, synapse: core.protocol.PatternQueryAck) -> float:
        return await self._priority(synapse)

    async def priority_pattern_query(self, synapse: core.protocol.PatternQuery) -> float:
        return await self._priority(synapse)

    async def _priority(self, synapse: core.protocol.PatternQuery | core.protocol.PatternQueryAck) -> float:

        if synapse.dendrite is None or synapse.dendrite.hotkey is None:
            bt.logging.warning(
                "Received a request without a dendrite or hotkey."
            )
            return 0.0

        caller_uid = self.metagraph.hotkeys.index(
            synapse.dendrite.hotkey
        )  # Get the caller index.
        priority = float(
            self.metagraph.S[caller_uid]
        )  # Return the stake as the priority.
        bt.logging.trace(
            f"Prioritizing {synapse.dendrite.hotkey} with value: {priority}"
        )
        return priority


if __name__ == "__main__":
    terminate_event = asyncio.Event()

    def signal_handler(sig, frame):
        bt.logging.info(
            "Shutdown signal received",
            extra={
                "signal": sig,
                "graceful_shutdown": True
            }
        )
        terminate_event.set()

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    with Miner() as miner:
        while not terminate_event.is_set():
            time.sleep(5)
