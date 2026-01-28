#!/usr/bin/env python3
"""GUI-002: Tray Status and DND/Focus Toggle"""

from typing import Dict, Any
from enum import Enum


class FocusMode(Enum):
    """Focus mode states"""
    NORMAL = "normal"
    DND = "dnd"
    FOCUS = "focus"
    PRIORITY = "priority"


class TrayStatus:
    """Tray status indicator"""

    def __init__(self):
        """Initialize tray status"""
        self.focus_mode = FocusMode.NORMAL
        self.is_active = True
        self.notification_count = 0
        self.status_message = "Ready"

    def set_focus_mode(self, mode: FocusMode) -> Dict[str, Any]:
        """Set focus mode"""
        previous = self.focus_mode
        self.focus_mode = mode

        messages = {
            FocusMode.NORMAL: "Normal mode - all notifications",
            FocusMode.DND: "Do Not Disturb - notifications silenced",
            FocusMode.FOCUS: "Focus mode - critical only",
            FocusMode.PRIORITY: "Priority mode - VIP only"
        }

        self.status_message = messages[mode]

        return {
            'previous_mode': previous.value,
            'new_mode': mode.value,
            'message': self.status_message,
            'changed': True
        }

    def toggle_dnd(self) -> Dict[str, Any]:
        """Toggle Do Not Disturb"""
        if self.focus_mode == FocusMode.DND:
            return self.set_focus_mode(FocusMode.NORMAL)
        else:
            return self.set_focus_mode(FocusMode.DND)

    def toggle_focus(self) -> Dict[str, Any]:
        """Toggle focus mode"""
        if self.focus_mode == FocusMode.FOCUS:
            return self.set_focus_mode(FocusMode.NORMAL)
        else:
            return self.set_focus_mode(FocusMode.FOCUS)

    def add_notification(self) -> None:
        """Add notification"""
        self.notification_count += 1

    def clear_notifications(self) -> None:
        """Clear all notifications"""
        self.notification_count = 0

    def get_status(self) -> Dict[str, Any]:
        """Get current tray status"""
        return {
            'active': self.is_active,
            'focus_mode': self.focus_mode.value,
            'status_message': self.status_message,
            'pending_notifications': self.notification_count,
            'dnd_enabled': self.focus_mode == FocusMode.DND,
            'focus_enabled': self.focus_mode == FocusMode.FOCUS
        }

    def set_active(self, active: bool) -> None:
        """Set active state"""
        self.is_active = active
        if active:
            self.status_message = "Active"
        else:
            self.status_message = "Inactive"


class M1StatusBar:
    """M1 macOS status bar integration"""

    def __init__(self):
        """Initialize M1 status bar"""
        self.tray = TrayStatus()
        self.menu_items = []

    def add_menu_item(self, label: str, action: str) -> None:
        """Add menu item"""
        self.menu_items.append({'label': label, 'action': action})

    def build_menu(self) -> Dict[str, Any]:
        """Build status bar menu"""
        return {
            'status': self.tray.get_status(),
            'menu_items': self.menu_items,
            'focus_toggle': {
                'label': f"Focus: {self.tray.focus_mode.value}",
                'available': True
            }
        }

    def render(self) -> Dict[str, Any]:
        """Render status bar"""
        return {
            'platform': 'macOS M1',
            'position': 'menu-bar',
            'menu': self.build_menu(),
            'icon_state': self.tray.focus_mode.value
        }
