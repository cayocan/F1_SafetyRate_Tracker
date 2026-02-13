"""Telemetry adapters for different F1 game versions"""
from .base_adapter import BaseAdapter, RaceState
from .f12019_adapter import F12019Adapter

__all__ = ['BaseAdapter', 'RaceState', 'F12019Adapter']
