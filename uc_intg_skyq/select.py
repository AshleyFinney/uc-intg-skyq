"""
SkyQ Select entities for Channels, Favourites, and Recordings.

Each is rendered as a Select widget on the Remote 3, exposing the corresponding
list of items as an independent entry point (rather than nesting under the
single media-player browse dropdown).

:copyright: (c) 2025-2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import logging
import re
from typing import Any

from ucapi import select, StatusCodes
from ucapi_framework import SelectEntity

from uc_intg_skyq.config import SkyQDeviceConfig
from uc_intg_skyq.const import DeviceState
from uc_intg_skyq.device import SkyQDevice

_LOG = logging.getLogger(__name__)

_CHANNEL_PREFIX_RE = re.compile(r"^(\d+)\s")


def _channel_no(item: object) -> str:
    return getattr(item, "channelno", "") or getattr(item, "lcn", "") or ""


def _format_channel_option(item: object) -> str:
    ch_no = _channel_no(item)
    name = getattr(item, "channelname", "") or "Channel"
    return f"{ch_no} - {name}" if ch_no else name


class _SkyQSelectBase(SelectEntity):
    """Common state-syncing scaffolding for Sky Q select entities."""

    def __init__(
        self,
        device_config: SkyQDeviceConfig,
        device: SkyQDevice,
        suffix: str,
        label: str,
    ) -> None:
        self._device = device
        entity_id = f"select.skyq_{device_config.identifier}.{suffix}"
        super().__init__(
            entity_id,
            f"{device_config.name} {label}",
            attributes={
                select.Attributes.STATE: select.States.UNAVAILABLE,
                select.Attributes.CURRENT_OPTION: "",
                select.Attributes.OPTIONS: [],
            },
            cmd_handler=self._handle_command,
        )
        self.subscribe_to_device(device)
        _LOG.info("[%s] Constructed and subscribed to device", entity_id)

    async def _fetch_options(self) -> list[str]:
        raise NotImplementedError

    async def _handle_select_option(self, option: str) -> StatusCodes:
        raise NotImplementedError

    async def sync_state(self) -> None:
        _LOG.info(
            "[%s] sync_state called (device.state=%s, cached options=%d)",
            self.id,
            self._device.state,
            len(self.select_options or []),
        )
        if self._device.state == DeviceState.UNAVAILABLE:
            self.set_state(select.States.UNAVAILABLE, update=True)
            return
        options = self.select_options
        if not options:
            try:
                options = await self._fetch_options()
            except Exception as err:
                _LOG.warning("[%s] Failed to fetch options: %s", self.id, err)
                self.set_state(select.States.UNKNOWN, update=True)
                return
            _LOG.info("[%s] Loaded %d options from device", self.id, len(options))
        # Always push state+options so a newly-configured entity gets data on
        # the next poll cycle (the framework no-ops update for unconfigured
        # entities, so the local cache could otherwise stay stuck on the
        # Remote even after the user adds the widget).
        self.set_attributes(state=select.States.ON, options=options, update=True)
        _LOG.info("[%s] Pushed %d options to Remote", self.id, len(options))

    async def _handle_command(
        self,
        entity: select.Select,
        cmd_id: str,
        params: dict[str, Any] | None,
    ) -> StatusCodes:
        _LOG.debug("[%s] Command: %s params=%s", self.id, cmd_id, params)
        if cmd_id != select.Commands.SELECT_OPTION:
            return StatusCodes.NOT_IMPLEMENTED
        option = (params or {}).get("option", "")
        if not option:
            return StatusCodes.BAD_REQUEST
        return await self._handle_select_option(option)


class _ChannelLikeSelect(_SkyQSelectBase):
    """Base for selects whose options are channels (tune-on-pick)."""

    async def _handle_select_option(self, option: str) -> StatusCodes:
        match = _CHANNEL_PREFIX_RE.match(option)
        if not match:
            _LOG.warning(
                "[%s] Could not parse channel number from option %r", self.id, option
            )
            return StatusCodes.BAD_REQUEST
        channel_no = match.group(1)
        result = await self._device.cmd_change_channel(channel_no)
        if result:
            self.set_current_option(option, update=True)
        return StatusCodes.OK if result else StatusCodes.SERVER_ERROR


class SkyQChannelsSelect(_ChannelLikeSelect):
    """Select entity exposing the full Sky Q channel list for direct tuning."""

    def __init__(self, device_config: SkyQDeviceConfig, device: SkyQDevice) -> None:
        super().__init__(device_config, device, suffix="channels", label="Channels")

    async def _fetch_options(self) -> list[str]:
        items = await self._device.get_channel_list()
        return [_format_channel_option(c) for c in items if _channel_no(c)]


class SkyQFavouritesSelect(_ChannelLikeSelect):
    """Select entity exposing the Sky Q favourites list for direct tuning."""

    def __init__(self, device_config: SkyQDeviceConfig, device: SkyQDevice) -> None:
        super().__init__(device_config, device, suffix="favourites", label="Favourites")

    async def _fetch_options(self) -> list[str]:
        items = await self._device.get_favourite_list()
        return [_format_channel_option(f) for f in items if _channel_no(f)]


class SkyQRecordingsSelect(_SkyQSelectBase):
    """
    Select entity exposing recordings as an informational list.

    Selection does NOT trigger playback — Sky Q deliberately locks down
    external recording playback (no REST endpoint, UPnP transport returns
    "TRANSPORT IS LOCKED", no IRCC code for the planner button). The widget
    is a viewer only: picking an option updates current_option but performs
    no action on the box.
    """

    def __init__(self, device_config: SkyQDeviceConfig, device: SkyQDevice) -> None:
        super().__init__(device_config, device, suffix="recordings", label="Recordings")

    async def _fetch_options(self) -> list[str]:
        recordings = await self._device.get_recordings()
        return [getattr(r, "title", "") or "Recording" for r in recordings]

    async def _handle_select_option(self, option: str) -> StatusCodes:
        _LOG.info(
            "[%s] Recording '%s' selected (informational only — Sky Q does not "
            "support remote-triggered recording playback)", self.id, option,
        )
        self.set_current_option(option, update=True)
        return StatusCodes.OK
