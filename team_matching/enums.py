from enum import Enum

class ExperienceLevel(Enum):
    JUNIOR = 1
    MID = 2
    SENIOR = 3
    LEAD = 4
    ARCHITECT = 5

class ProjectPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class AvailabilityStatus(Enum):
    AVAILABLE = 1
    PARTIALLY_AVAILABLE = 2
    BUSY = 3
    UNAVAILABLE = 4
