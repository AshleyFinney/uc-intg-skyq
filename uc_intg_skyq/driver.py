"""
SkyQ Integration Driver.

:copyright: (c) 2025-2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import logging

from ucapi_framework import BaseIntegrationDriver

from uc_intg_skyq.config import SkyQDeviceConfig
from uc_intg_skyq.device import SkyQDevice
from uc_intg_skyq.media_player import SkyQMediaPlayer
from uc_intg_skyq.remote import SkyQRemote
# SkyQAppsSelect is intentionally NOT imported/registered here. Sky Q has no
# programmatic app-launch path (verified against pyskyqremote, skyq-ha,
# pyskyq-bradwood, sky-remote-archerjm, go-skyremote, alexa-sky-hd, plus a
# direct probe of /as/apps/* — every endpoint returned 404). The class is
# kept in select.py only as a record of what was tried.
from uc_intg_skyq.select import (
    SkyQChannelsSelect,
    SkyQFavouritesSelect,
    SkyQRadioSelect,
    SkyQRecordingsSelect,
)
from uc_intg_skyq.sensor import (
    SkyQChannelSensor,
    SkyQConnectionTypeSensor,
    SkyQHdrCapableSensor,
    SkyQIPAddressSensor,
    SkyQMediaKindSensor,
    SkyQModelSensor,
    SkyQSerialSensor,
    SkyQSoftwareVersionSensor,
    SkyQUhdCapableSensor,
    SkyQUptimeSensor,
)

_LOG = logging.getLogger(__name__)


class SkyQDriver(BaseIntegrationDriver[SkyQDevice, SkyQDeviceConfig]):
    """Integration driver for SkyQ satellite boxes."""

    def __init__(self) -> None:
        super().__init__(
            device_class=SkyQDevice,
            entity_classes=[
                SkyQMediaPlayer,
                SkyQRemote,
                SkyQModelSensor,
                SkyQIPAddressSensor,
                SkyQChannelSensor,
                SkyQConnectionTypeSensor,
                SkyQSerialSensor,
                SkyQSoftwareVersionSensor,
                SkyQHdrCapableSensor,
                SkyQUhdCapableSensor,
                SkyQUptimeSensor,
                SkyQMediaKindSensor,
                SkyQChannelsSelect,
                SkyQFavouritesSelect,
                SkyQRadioSelect,
                SkyQRecordingsSelect,
            ],
            driver_id="uc_intg_skyq",
            require_connection_before_registry=False,
        )
