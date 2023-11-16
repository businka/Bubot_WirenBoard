from bubot.OcfResource.OcfResource import OcfResource


class OicRLightBrightness(OcfResource):
    async def on_get(self, request):
        prefix, number = request.uri_path.split('/')
        await self.device.retrieve_switch(number)
        return await super().on_get(request)

    async def on_post(self, request, response):
        self.debug('post', request)
        prefix, number = request.uri_path.split('/')
        payload = request.decode_payload()
        if 'value' in payload:
            await self.device.update_switch(number, payload['value'])
        return await super().on_post(request, response)
