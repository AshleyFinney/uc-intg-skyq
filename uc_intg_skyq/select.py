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
        # ucapi stores the entity object itself in configured_entities, not a
        # copy — so configured_entity.attributes and self.attributes are the
        # SAME dict. The framework's SelectEntity.set_attributes/set_state
        # helpers mutate self.attributes BEFORE calling update(), which means
        # filter_changed_attributes compares the new dict against itself,
        # finds nothing changed, and silently skips the wire push. Bypass the
        # helpers and call self.update({...fresh dict...}) so the filter has
        # something to compare against.
        if self._device.state == DeviceState.UNAVAILABLE:
            self.update({select.Attributes.STATE: select.States.UNAVAILABLE})
            return
        if not self._api.configured_entities.contains(self.id):
            _LOG.info("[%s] Not configured yet, skipping sync", self.id)
            return
        options = self.select_options
        if not options:
            try:
                options = await self._fetch_options()
            except Exception as err:
                _LOG.warning("[%s] Failed to fetch options: %s", self.id, err)
                self.update({select.Attributes.STATE: select.States.UNKNOWN})
                return
            _LOG.info("[%s] Loaded %d options from device", self.id, len(options))
        self.update({
            select.Attributes.STATE: select.States.ON,
            select.Attributes.OPTIONS: options,
        })
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
            self.update({select.Attributes.CURRENT_OPTION: option})
        return StatusCodes.OK if result else StatusCodes.SERVER_ERROR


class SkyQChannelsSelect(_ChannelLikeSelect):
    """Select entity exposing TV channels for direct tuning (excludes radio)."""

    def __init__(self, device_config: SkyQDeviceConfig, device: SkyQDevice) -> None:
        super().__init__(device_config, device, suffix="channels", label="Channels")

    async def _fetch_options(self) -> list[str]:
        items = await self._device.get_channel_list()
        return [
            _format_channel_option(c) for c in items
            if _channel_no(c) and getattr(c, "channeltype", "") != "audio"
        ]


class SkyQRadioSelect(_ChannelLikeSelect):
    """Select entity exposing radio channels for direct tuning."""

    def __init__(self, device_config: SkyQDeviceConfig, device: SkyQDevice) -> None:
        super().__init__(device_config, device, suffix="radio", label="Radio")

    async def _fetch_options(self) -> list[str]:
        items = await self._device.get_channel_list()
        return [
            _format_channel_option(c) for c in items
            if _channel_no(c) and getattr(c, "channeltype", "") == "audio"
        ]


class SkyQFavouritesSelect(_ChannelLikeSelect):
    """Select entity exposing the Sky Q favourites list for direct tuning."""

    def __init__(self, device_config: SkyQDeviceConfig, device: SkyQDevice) -> None:
        super().__init__(device_config, device, suffix="favourites", label="Favourites")

    async def _fetch_options(self) -> list[str]:
        items = await self._device.get_favourite_list()
        return [_format_channel_option(f) for f in items if _channel_no(f)]


class SkyQAppsSelect(_SkyQSelectBase):
    """
    Select entity exposing installed Sky Q apps for launch (experimental).

    pyskyqremote can read installed apps and detect the active one but does
    not expose a launch API — Sky Q's HTTP launch endpoint is undocumented.
    On select_option we try a handful of plausible HTTP patterns; whichever
    (if any) the box accepts is logged at INFO level. Worst case: we discover
    Sky Q rejects all of them and the select becomes informational.
    """

    def __init__(self, device_config: SkyQDeviceConfig, device: SkyQDevice) -> None:
        super().__init__(device_config, device, suffix="apps", label="Apps")
        self._title_to_app_id: dict[str, str] = {}

    async def _fetch_options(self) -> list[str]:
        apps = await self._device.get_apps()
        self._title_to_app_id = {
            a.get("title"): a.get("appId")
            for a in apps
            if a.get("title") and a.get("appId")
        }
        titles = sorted(self._title_to_app_id.keys(), key=str.lower)
        _LOG.info(
            "[%s] Built app map: %d apps, sample appIds: %s",
            self.id, len(titles), list(self._title_to_app_id.values())[:3],
        )
        return titles

    async def _handle_select_option(self, option: str) -> StatusCodes:
        app_id = self._title_to_app_id.get(option)
        _LOG.info(
            "[%s] select_option: title=%r → appId=%r (cache size=%d)",
            self.id, option, app_id, len(self._title_to_app_id),
        )
        if not app_id:
            return StatusCodes.BAD_REQUEST
        result = await self._device.cmd_launch_app(app_id)
        if result:
            self.update({select.Attributes.CURRENT_OPTION: option})
            _LOG.info("[%s] Launch reported success for %r", self.id, option)
            return StatusCodes.OK
        _LOG.warning(
            "[%s] Launch failed for title=%r appId=%s — Sky Q likely doesn't "
            "expose a launch API on this firmware",
            self.id, option, app_id,
        )
        return StatusCodes.SERVER_ERROR


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
        self.update({select.Attributes.CURRENT_OPTION: option})
        return StatusCodes.OK
