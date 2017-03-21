import json
import logging
import base64
import aiohttp

from aiohttp.web import Request
from OpenSSL.crypto import verify, load_publickey, FILETYPE_PEM, X509
from OpenSSL.crypto import Error as SignatureError

from opsdroid.matchers import match_webhook
from opsdroid.message import Message


_LOGGER = logging.getLogger(__name__)


@match_webhook("event")
async def event(opsdroid, config, message):
    if type(message) is not Message and type(message) is Request:

        # Capture the request POST data
        request = await message.post()

        # Verify webhook has come form travis CI
        signature = get_signature(message)
        public_key = await get_travis_public_key(config.get("travis_endpoint", "org"))
        try:
            check_authorized(signature, public_key, request["payload"])
        except SignatureError:
            _LOGGER.error("Unauthorized request. Unable to verify sender as Travis CI.")
            return

        # Set message to a default message
        message = Message("",
                          None,
                          config.get("room", opsdroid.default_connector.default_room),
                          opsdroid.default_connector)

        # Unpack payload
        payload = json.loads(request["payload"])
        _LOGGER.debug(payload)

        # Respond
        await message.respond("Build {} of {}/{} has {}.".format(
            payload["number"],
            payload["repository"]["owner_name"],
            payload["repository"]["name"],
            payload["status_message"].lower()))
        await message.respond(payload["build_url"])


def check_authorized(signature, public_key, payload):
    """
    Convert the PEM encoded public key to a format palatable for pyOpenSSL,
    then verify the signature.
    """
    pkey_public_key = load_publickey(FILETYPE_PEM, public_key)
    certificate = X509()
    certificate.set_pubkey(pkey_public_key)
    verify(certificate, signature, payload, str('sha1'))


def get_signature(request):
    """
    Extract the raw bytes of the request signature provided by travis.
    """
    signature = request.headers['Signature']
    return base64.b64decode(signature)


async def get_travis_public_key(endpoint):
    """
    Returns the PEM encoded public key from the Travis CI /config endpoint
    """
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.travis-ci.{}/config".format(endpoint)) as resp:
            data = await resp.json()
            return data['config']['notifications']['webhook']['public_key']
