#
# Copyright (c) 2016 Nordic Semiconductor ASA
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#   1. Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
#   2. Redistributions in binary form must reproduce the above copyright notice, this
#   list of conditions and the following disclaimer in the documentation and/or
#   other materials provided with the distribution.
#
#   3. Neither the name of Nordic Semiconductor ASA nor the names of other
#   contributors to this software may be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
#   4. This software must only be used in or with a processor manufactured by Nordic
#   Semiconductor ASA, or in or with a processor manufactured by a third party that
#   is used in combination with a processor manufactured by Nordic Semiconductor.
#
#   5. Any software provided in binary or object form under this license must not be
#   reverse engineered, decompiled, modified and/or disassembled.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# Python specific imports
import abc
import logging

# Nordic Semiconductor imports

logger = logging.getLogger(__name__)


class DfuEvent:
    PROGRESS_EVENT = 1


class DfuTransport(object, metaclass=abc.ABCMeta):
    """
    This class as an abstract base class inherited from when implementing transports.

    The class is generic in nature, the underlying implementation may have missing semantic
    than this class describes. But the intent is that the implementer shall follow the semantic as
    best as she can.
    """

    OP_CODE = {
        'CreateObject'          : 0x01,
        'SetPRN'                : 0x02,
        'CalcChecSum'           : 0x03,
        'Execute'               : 0x04,
        'ReadError'             : 0x05,
        'ReadObject'            : 0x06,
        'Response'              : 0x60,
    }

    RES_CODE = {
        'InvalidCode'           : 0x00,
        'Success'               : 0x01,
        'NotSupported'          : 0x02,
        'InvalidParameter'      : 0x03,
        'InsufficientResources' : 0x04,
        'InvalidObject'         : 0x05,
        'InvalidSignature'      : 0x06,
        'UnsupportedType'       : 0x07,
        'OperationNotPermitted' : 0x08,
        'OperationFailed'       : 0x0A,
        'ExtendedError'         : 0x0B,
    }

    @abc.abstractmethod
    def __init__(self):
        self.callbacks = {}


    @abc.abstractmethod
    def open(self):
        """
        Open a port if appropriate for the transport.
        :return:
        """
        pass


    @abc.abstractmethod
    def close(self):
        """
        Close a port if appropriate for the transport.
        :return:
        """
        pass

    @abc.abstractmethod
    def send_init_packet(self, init_packet):
        """
        Send init_packet to device.

        This call will block until init_packet is sent and transfer of packet is complete.

        :param init_packet: Init packet as a str.
        :return:
        """
        pass


    @abc.abstractmethod
    def send_firmware(self, firmware):
        """
        Start sending firmware to device.

        This call will block until transfer of firmware is complete.

        :param firmware:
        :return:
        """
        pass


    def register_events_callback(self, event_type, callback):
        """
        Register a callback.

        :param DfuEvent callback:
        :return: None
        """
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []

        self.callbacks[event_type].append(callback)


    def _send_event(self, event_type, **kwargs):
        """
        Method for sending events to registered callbacks.

        If callbacks throws exceptions event propagation will stop and this method be part of the track trace.

        :param DfuEvent event_type:
        :param kwargs: Arguments to callback function
        :return:
        """
        if event_type in list(self.callbacks.keys()):
            for callback in self.callbacks[event_type]:
                callback(**kwargs)
