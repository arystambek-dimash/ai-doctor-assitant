from pydantic import BaseModel, Field


class AdminStatsResponse(BaseModel):
    total_users: int = Field(..., alias="totalUsers")
    total_doctors: int = Field(..., alias="totalDoctors")
    total_bookings: int = Field(..., alias="totalBookings")
    today_bookings: int = Field(..., alias="todayBookings")
    pending_bookings: int = Field(..., alias="pendingBookings")
    completed_bookings: int = Field(..., alias="completedBookings")
    total_emrs: int = Field(..., alias="totalEMRs")

    class Config:
        populate_by_name = True
        from_attributes = True
