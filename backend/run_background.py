import asyncio
from sanic.log import logger
from repositories.reservation_repository import ReservationRepository
from repositories.spot_repository import SpotRepository
from repositories.user_repository import UserRepository
from services.reservation_service import ReservationService

async def cleanup_loop(app):
    while True:
        try:
            async with app.ctx.Session() as session:
                reservation_repo = ReservationRepository(session)
                spot_repo = SpotRepository(session)
                user_repo = UserRepository(session)
                service = ReservationService(session, reservation_repo, spot_repo, user_repo)
                
                await service.release_expired_checkins()
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
            
        # Run every 5 minutes
        await asyncio.sleep(300)

def start_cleanup_task(app):
    return cleanup_loop(app)
