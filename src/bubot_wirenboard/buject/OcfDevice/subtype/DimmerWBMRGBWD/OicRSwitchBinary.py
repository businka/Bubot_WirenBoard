from bubot.OcfResource.OcfResource import OcfResource
from Bubot_CoAP.defines import Codes


class OicRSwitchBinary(OcfResource):
    async def on_get(self, request):
        await self.device.power_retrieve()
        return await super().on_get(request)

    async def on_post(self, request, response):
        self.debug('post', request)
        payload = request.decode_payload()
        if 'value' in payload:
            await self.device.power_update(payload['value'])
        return await super().on_post(request, response)
