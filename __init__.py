import json
import logging

from aiohttp.web import Request

from opsdroid.matchers import match_webhook
from opsdroid.message import Message


_LOGGER = logging.getLogger(__name__)


@match_webhook("event")
async def event(opsdroid, config, message):
    if type(message) is not Message and type(message) is Request:
        # Capture the request POST data and set message to a default message
        request = await message.post()
        message = Message("",
                          None,
                          config.get("room", opsdroid.default_connector.default_room),
                          opsdroid.default_connector)

        payload = json.loads(request["payload"])
        _LOGGER.debug(payload)

        # Respond
        await message.respond("Build {} of {}/{} has {}.".format(
            payload["number"],
            payload["repository"]["owner_name"],
            payload["repository"]["name"],
            payload["status_message"].lower()))
        await message.respond(payload["build_url"])
