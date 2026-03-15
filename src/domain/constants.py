from enum import Enum
from enum import StrEnum


class UserRole(StrEnum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"


class DoctorStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class VisitType(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"


class ChatSessionStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"


class ChatSource(str, Enum):
    WEB = "web"
    MOBILE = "mobile"
    ADMIN = "admin"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ContentType(str, Enum):
    TEXT = "text"
    JSON = "json"
    EVENT = "event"


class TriageStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"


class UrgencyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
