import asyncio
import logging
import unittest
from datetime import datetime

from bubot.core.TestHelper import wait_run_device, wait_cancelled_device
from bubot_modbus.buject.OcfDevice.subtype.SerialServerHF511.SerialServerHF511 import SerialServerHF511 as ModbusDevice
from bubot_wirenboard.buject.OcfDevice.subtype.DimmerWBLED.DimmerWBLED import DimmerWBLED as Device

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger = logging.getLogger('Bubot_CoAP')
logger.setLevel(logging.ERROR)


class TestDimmerWBLED(unittest.IsolatedAsyncioTestCase):
    pass
    net_interface = "192.168.1.11"
    config = {
        '/oic/con': {
            'master': dict(),
            'slave': 152,
            'baudRate': 9600,
            'parity': 'None',
            'dataBits': 8,
            'stopBits': 2,
            'udpCoapIPv6': None
        }

    }
    bad_ip_config = {
        "/oic/d": {
            "di": "1"
        },
        "/oic/con": {
            "master": {
                # "anchor": "ocf://6d350e5d-8b7c-459e-a671-e5860b318796",
                "di": "6d350e5d-8b7c-459e-a671-e5860b318796",
                "href": "/modbus_msg",
                "eps": [
                    {
                        "ep": "coap://192.168.1.11:61169",
                        "net_interface": "192.168.1.11"
                    }
                ]
            },
            "slave": 113
        }
    }
    modbus_config = {
        '/oic/con': {
            'host': '192.168.1.25',
            'port': 502,
            'baudRate': 9600,
            'parity': 0,
            'dataBits': 8,
            'stopBits': 2,
            'udpCoapIPv4': True,
            'udpCoapIPv6': False
        }
    }

    async def asyncSetUp(self) -> None:
        self.modbus_device = ModbusDevice.init_from_file(di='2')
        self.modbus_task = await wait_run_device(self.modbus_device)
        self.config['/oic/con']['master']['anchor'] = self.modbus_device.link['anchor']
        self.config['/oic/con']['master']['eps'] = self.modbus_device.link['eps']
        self.config['/oic/con']['master']['eps'][0]['net_interface'] = self.net_interface
        self.device = Device.init_from_config(self.config, di='1')
        self.device_task = await wait_run_device(self.device)

    async def asyncTearDown(self) -> None:
        await wait_cancelled_device(self.device, self.device_task)
        await wait_cancelled_device(self.modbus_device, self.modbus_task)

    async def test_init(self):
        self.assertIn('/light', self.device.data)
        self.assertListEqual(self.device.data['/light']['rt'], ['oic.r.switch.binary', 'oic.r.light.brightness'])

    async def test_on_init(self):
        await self.device.on_init()
        pass

    @unittest.skip
    async def test_reconnect_to_new_ip(self):
        modbus_device0 = ModbusDevice.init_from_file(di='1')
        modbus_device = ModbusDevice.init_from_file(di='2')
        modbus_task = await wait_run_device(modbus_device)
        device = Device.init_from_config(self.bad_ip_config)
        device_task = await wait_run_device(device)
        await wait_cancelled_device(device, device_task)
        await wait_cancelled_device(modbus_device, modbus_task)
        await wait_cancelled_device(modbus_device0, modbus_task)

    async def test_retrieve_switch(self):
        res = await self.device.power_retrieve()
        value1 = res['value']
        res = await self.device.power_update(not value1)
        value2 = res['value']
        pass

    async def test_update_brightness(self):
        brightness = 0
        message = OcfRequest(op='update', to=dict(href='/brightness'), cn=dict(brightness=brightness))
        result = await self.device.on_post_request(message)
        self.assertEqual(result['brightness'], brightness)
        pass

    async def test_update_switch(self):
        value = False
        message = OcfRequest(op='update', to=dict(href='/power'), cn=dict(value=value))
        result = await self.device.on_post_request(message)
        self.assertEqual(result['value'], value)

    async def test_echo_get_light_baseline(self):
        await self.device.run()
        from aio_modbus_client.ModbusProtocolEcho import ModbusProtocolEcho
        while self.device.get_param('/oic/con', 'status_code') == 'load':
            await asyncio.sleep(0.1)
        self.device.modbus.protocol = ModbusProtocolEcho({
            '\x00\x02\x00\x01': '\x01\x00\x01'
        })
        result = await self.device.modbus.read_param('level_blue')
        pass

    async def test_get_light_baseline(self):
        main = await self.device.run()
        await main
        # while self.device.get_props('/oic/con', 'status_code') == 'load':
        #     await asyncio.sleep(0.1)
        result = await self.device.modbus.read_param('level_blue')
        pass

    def test_get_light1_baseline(self):
        self.device = Device.init_from_config(None, dict(handler=Device.__name__, data=self.config))
        message = OcfRequest(**dict(operation='get', uri='/light'))
        result = self.device.on_get_request(message)
        pass

    def test_set_light_baseline(self):
        self.device = Device.init_from_config(self.config)
        data = dict(value=True, brightness=100)
        message = OcfRequest(**dict(operation='update', uri_path=['light'], data=data))
        self.device.on_init()
        result = self.device.on_post_request(message)
        self.assertDictEqual(result, data)

    def test_get_light_brightness(self):
        self.device = Device.init_from_config(None, dict(handler=Device.__name__, data=self.config))
        message = OcfRequest(**dict(operation='get', uri='/light', query={'rt': ['oic.r.light.brightness']}))
        self.device.on_get_request(message)

        # self.OcfDevice.run()
        pass

    async def test_run(self):
        await self.device.run()
        # result = await self.device.coap.discovery_resource()
        await asyncio.sleep(600)
        pass

    async def test_discovery(self):
        await self.device.run()
        result = await self.device.coap.discovery_resource()
        await asyncio.sleep(600)
        pass

    async def test_local_discovery(self):
        msg = OcfRequest(**dict(
            uri_path=['oic', 'res'],
            operation='get'
        ))
        res = self.device.on_get_request(msg)
        await asyncio.sleep(600)
        pass

    async def test_maximum_load(self):
        modbus_device = ModbusDevice.init_from_file('SerialServerHF511', '2')
        modbus_task = await wait_run_device(modbus_device)
        self.config['/oic/con']['master']['anchor'] = modbus_device.link['anchor']
        self.config['/oic/con']['master']['eps'] = modbus_device.link['eps']
        device = Device.init_from_config(self.config, path=self.config_path)
        device_task = await wait_run_device(device)
        task = []
        count = 50
        for i in range(50):
            message = OcfRequest(op='retrieve', to=dict(href='/power'))
            task.append(device.on_get_request(message))
        begin = datetime.now()
        result = await asyncio.gather(*task)
        end = datetime.now()
        print(end - begin)
        await wait_cancelled_device(device, device_task)
        await wait_cancelled_device(modbus_device, modbus_task)

    async def test_retrieve_model(self):
        res = await self.device.modbus.is_device()
        self.assertTrue(res)

    async def test_find_devices(self):
        res = await self.device.find_devices(notify=notify)
        pass


async def notify(data):
    print(data)
