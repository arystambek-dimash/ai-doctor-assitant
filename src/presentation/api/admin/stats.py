from fastapi import APIRouter, Depends

from src.domain.entities.users import UserEntity
from src.presentation.api.schemas.responses.stats import AdminStatsResponse
from src.presentation.dependencies import get_stats_use_case, requires_roles
from src.use_cases.stats.use_case import StatsUseCase

router = APIRouter(prefix="/admin/stats", tags=["Admin Stats"])


@router.get("", response_model=AdminStatsResponse)
async def get_admin_stats(
        use_case: StatsUseCase = Depends(get_stats_use_case),
        current_user: UserEntity = Depends(requires_roles(is_admin=True)),
):
    """
    Get admin dashboard statistics.
    Includes counts for users, doctors, appointments, and medical records.
    """
    stats = await use_case.get_admin_stats()
    return AdminStatsResponse(
        totalUsers=stats.total_users,
        totalDoctors=stats.total_doctors,
        totalBookings=stats.total_bookings,
        todayBookings=stats.today_bookings,
        pendingBookings=stats.pending_bookings,
        completedBookings=stats.completed_bookings,
        totalEMRs=stats.total_emrs,
    )
