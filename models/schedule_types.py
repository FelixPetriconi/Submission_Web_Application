"""Support types for the conference schedule."""

from enum import Enum


class ConferenceDay(Enum):
    workshops = 'workshops'
    day_1 = '1'
    day_2 = '2'
    day_3 = '3'
    day_4 = '4'


class SessionSlot(Enum):
    session_1 = '1'
    session_2 = '2'
    session_3 = '3'


class QuickieSlot(Enum):
    slot_1 = '1'
    slot_2 = '2'
    slot_3 = '3'
    slot_4 = '4'


class Room(Enum):
    bristol_suite = 'Bristol Suite'
    bristol_1 = 'Bristol 1'
    bristol_2 = 'Bristol 2'
    bristol_3 = 'Bristol 3'
    empire = 'Empire'
    great_britain = 'SS Great Britain'
    wallace = 'Wallace'
    concorde = 'Concorde'
    old_vic = 'Old Vic'
    castle_view = 'Castle View'
    conservatory = 'Conservatory'
