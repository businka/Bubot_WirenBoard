import unittest
from BubotObj.OcfDevice.subtype.DimmerWBMRGBWD.DimmerWBMRGBWD import DimmerWBMRGBWD as Device
from BubotObj.OcfDevice.subtype.SerialServerHF511.SerialServerHF511 import SerialServerHF511 as ModbusDevice
from Bubot.Core.OcfMessage import OcfRequest
from Bubot.Core.TestHelper import async_test, wait_run_device, get_config_path, wait_cancelled_device
import logging
import asyncio
from datetime import datetime


class TestDimmerWBMRGBWD(unittest.TestCase):
    pass
    config = {
        '/oic/con': {
            'master': dict(href='/modbus_msg'),
            'slave': 113,  # 0x71,
            'baudRate': 9600,
            'parity': 'None',
            'dataBits': 8,
            'stopBits': 2,
            'udpCoapPort': 17771,
            'udpCoapIPv4': True,
            'udpCoapIPv6': False
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
                        "ep": "coap://[2a00:84c0:300:19b0:519d:fc33:2aa7:1111]:61169"
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
            'udpCoapPort': 17772,
            'udpCoapIPv4': True,
            'udpCoapIPv6': False
        }
    }

    @async_test
    async def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.config_path = get_config_path(__file__)
        pass

    @async_test
    async def test_init(self):
        self.assertIn('/light', self.device.data)
        self.assertListEqual(self.device.data['/light']['rt'], ['oic.r.switch.binary', 'oic.r.light.brightness'])

    @async_test
    async def test_on_init(self):
        await self.device.on_init()
        pass

    @async_test
    async def test_reconnect_to_new_ip(self):
        modbus_device = ModbusDevice.init_from_file(path='SerialServerHF511', di='2')
        modbus_task = await wait_run_device(modbus_device)
        device = Device.init_from_config(self.bad_ip_config)
        device_task = await wait_run_device(device)
        await wait_cancelled_device(device, device_task)
        await wait_cancelled_device(modbus_device, modbus_task)

    @async_test
    async def test_retrieve_switch(self):
        value = False
        modbus_device = ModbusDevice.init_from_file(path='./config/', di='2')
        modbus_task = await wait_run_device(modbus_device)
        self.config['/oic/con']['master']['anchor'] = modbus_device.link['anchor']
        self.config['/oic/con']['master']['eps'] = modbus_device.link['eps']
        self.device = Device.init_from_config(self.config, path=self.config_path)
        device_task = await wait_run_device(self.device)
        message = OcfRequest(op='retrieve', to=dict(href='/power'))
        result = await self.device.on_get_request(message)
        print(result.get('value'))
        self.assertEqual(result['value'], value)
        pass

    @async_test
    async def test_retrieve_color(self):
        modbus_device = ModbusDevice.init_from_config(self.modbus_config, path=self.config_path)
        modbus_task = await wait_run_device(modbus_device)
        self.config['/oic/con']['master'] = modbus_device.link
        self.device = Device.init_from_config(self.config, path=self.config_path)
        device_task = await wait_run_device(self.device)
        message = OcfRequest(op='retrieve', to=dict(href='/color'))
        result = await self.device.on_get_request(message)
        print(result)
        # self.assertEqual(result['color'], value)
        modbus_task.cancel()
        device_task.cancel()
        await modbus_task
        await device_task

        pass

    @async_test
    async def test_update_brightness(self):
        brightness = 0
        modbus_device = ModbusDevice.init_from_config(self.modbus_config, path=self.config_path)
        modbus_task = await wait_run_device(modbus_device)
        self.config['/oic/con']['master'] = modbus_device.link
        self.device = Device.init_from_config(self.config, path=self.config_path)
        device_task = await wait_run_device(self.device)
        message = OcfRequest(op='update', to=dict(href='/brightness'), cn=dict(brightness=brightness))
        result = await self.device.on_post_request(message)
        self.assertEqual(result['brightness'], brightness)
        modbus_task.cancel()
        device_task.cancel()
        pass

    @async_test
    async def test_update_switch(self):
        value = False
        modbus_device = ModbusDevice.init_from_config(self.modbus_config, path=self.config_path)
        modbus_task = await wait_run_device(modbus_device)
        self.config['/oic/con']['master'] = modbus_device.link
        self.device = Device.init_from_config(self.config, path=self.config_path)
        device_task = await wait_run_device(self.device)
        message = OcfRequest(op='update', to=dict(href='/power'), cn=dict(value=value))
        result = await self.device.on_post_request(message)
        self.assertEqual(result['value'], value)
        modbus_task.cancel()
        device_task.cancel()
        pass

    @async_test
    async def test_find_devices(self):
        modbus_device = ModbusDevice.init_from_config(self.modbus_config, path=self.config_path)
        mobus_task = await wait_run_device(modbus_device)
        self.config['/oic/con']['master'] = modbus_device.link
        self.device = Device.init_from_config(self.config, path=self.config_path)
        device_task = await wait_run_device(self.device)
        res = await self.device.action_find_devices()
        pass

    @async_test
    async def test_is_device(self):
        brightness = 60
        modbus_device = ModbusDevice.init_from_config(self.modbus_config, path=self.config_path)
        mobus_task = await wait_run_device(modbus_device)
        self.config['/oic/con']['master'] = modbus_device.link
        self.device = Device.init_from_config(self.config, path=self.config_path)
        device_task = await wait_run_device(self.device)
        res = await self.device.modbus.is_device()
        self.assertTrue(res)
        pass

    @async_test
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

    @async_test
    async def test_get_light_baseline(self):
        main = await self.device.run()
        await main
        # while self.device.get_props('/oic/con', 'status_code') == 'load':
        #     await asyncio.sleep(0.1)
        result = await self.device.modbus.read_param('level_blue')
        pass

    @async_test
    def test_get_light1_baseline(self):
        self.device = Device.init_from_config(None, dict(handler=Device.__name__, data=self.config))
        message = OcfRequest(**dict(operation='get', uri='/light'))
        result = self.device.on_get_request(message)
        pass

    @async_test
    def test_set_light_baseline(self):
        self.device = Device.init_from_config(self.config)
        data = dict(value=True, brightness=100)
        message = OcfRequest(**dict(operation='update', uri_path=['light'], data=data))
        self.device.on_init()
        result = self.device.on_post_request(message)
        self.assertDictEqual(result, data)

    @async_test
    def test_get_light_brightness(self):
        self.device = Device.init_from_config(None, dict(handler=Device.__name__, data=self.config))
        message = OcfRequest(**dict(operation='get', uri='/light', query={'rt': ['oic.r.light.brightness']}))
        self.device.on_get_request(message)

        # self.OcfDevice.run()
        pass

    @async_test
    async def test_run(self):
        await self.device.run()
        # result = await self.device.coap.discovery_resource()
        await asyncio.sleep(600)
        pass

    @async_test
    async def test_discovery(self):
        await self.device.run()
        result = await self.device.coap.discovery_resource()
        await asyncio.sleep(600)
        pass

    @async_test
    async def test_local_discovery(self):
        msg = OcfRequest(**dict(
            uri_path=['oic', 'res'],
            operation='get'
        ))
        res = self.device.on_get_request(msg)
        await asyncio.sleep(600)
        pass

    @async_test
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
