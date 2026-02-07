#!/usr/bin/env python3
"""AAS-289: Home Assistant Integration"""

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass


class DeviceType(Enum):
    """Supported device types"""

    LIGHT = "light"
    SWITCH = "switch"
    SENSOR = "sensor"
    CLIMATE = "climate"
    COVER = "cover"
    LOCK = "lock"


@dataclass
class Device:
    """Home Assistant device representation"""

    id: str
    name: str
    type: DeviceType
    state: str
    attributes: Dict[str, Any]


class HomeAssistantIntegration:
    """Integration with Home Assistant"""

    def __init__(self, url: str, token: str):
        """Initialize HA integration"""
        self.url = url
        self.token = token
        self.devices: Dict[str, Device] = {}
        self.connected = False

    def connect(self) -> bool:
        """Connect to Home Assistant"""
        # Simulate connection
        self.connected = True
        return True

    def disconnect(self) -> None:
        """Disconnect from Home Assistant"""
        self.connected = False

    def get_devices(self) -> List[Device]:
        """Get all devices"""
        return list(self.devices.values())

    def add_device(self, device: Device) -> None:
        """Add device to registry"""
        self.devices[device.id] = device

    def turn_on(self, device_id: str) -> bool:
        """Turn on a device"""
        if device_id in self.devices:
            device = self.devices[device_id]
            device.state = "on"
            return True
        return False

    def turn_off(self, device_id: str) -> bool:
        """Turn off a device"""
        if device_id in self.devices:
            device = self.devices[device_id]
            device.state = "off"
            return True
        return False

    def set_brightness(self, device_id: str, level: int) -> bool:
        """Set brightness (0-255)"""
        if device_id in self.devices and 0 <= level <= 255:
            self.devices[device_id].attributes["brightness"] = level
            return True
        return False

    def get_temperature(self, sensor_id: str) -> Optional[float]:
        """Get temperature from sensor"""
        if sensor_id in self.devices:
            return self.devices[sensor_id].attributes.get("temperature")
        return None

    def set_temperature(self, climate_id: str, temp: float) -> bool:
        """Set target temperature"""
        if climate_id in self.devices:
            self.devices[climate_id].attributes["target_temp"] = temp
            return True
        return False

    def automate(self, trigger: str, action: str) -> Dict[str, Any]:
        """Create automation rule"""
        return {
            "id": f"auto_{trigger}_{action}",
            "trigger": trigger,
            "action": action,
            "enabled": True,
        }

    def get_state(self, device_id: str) -> Optional[str]:
        """Get device state"""
        if device_id in self.devices:
            return self.devices[device_id].state
        return None

    def listen_state_changes(self, device_id: str) -> bool:
        """Listen for state changes"""
        return device_id in self.devices

    def stats(self) -> Dict[str, Any]:
        """Get integration statistics"""
        by_type = {}
        for device in self.devices.values():
            dtype = device.type.value
            by_type[dtype] = by_type.get(dtype, 0) + 1

        return {
            "connected": self.connected,
            "device_count": len(self.devices),
            "devices_by_type": by_type,
        }
