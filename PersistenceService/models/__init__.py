"""
Models for Persistence Service

This module contains the data models that map to database tables.
"""

from .task import TaskRecord, TaskHistoryRecord
from .edge import EdgeRecord

__all__ = ['TaskRecord', 'TaskHistoryRecord', 'EdgeRecord']