from enum import Enum


class OrderAction(Enum):
    UNKNOWN = "unknown"
    DELIVERY = "delivery"
    TAKEAWAY = "takeaway"
    INSIDE = "inside"


class OrderStatus(Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    IN_DELIVERY = "in_delivery"
    COOKED = "cooked"
    DONE = "done"
    CANCELLED = "cancelled"
