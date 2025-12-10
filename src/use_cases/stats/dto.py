from dataclasses import dataclass


@dataclass
class AdminStatsDTO:
    total_users: int
    total_doctors: int
    total_bookings: int
    today_bookings: int
    pending_bookings: int
    completed_bookings: int
    total_emrs: int
