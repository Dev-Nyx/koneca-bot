from db.models import Player
from sqlalchemy import select
from datetime import datetime, timezone

class PlayerService:

    @staticmethod
    async def get_by_discord_id(session, discord_id: str):
        result = await session.execute(
            select(Player).where(Player.discord_id == discord_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_player(session, member):
        player = Player(
            discord_id=str(member.id),
            name=member.display_name,
            created_at=datetime.now(timezone.utc)
        )

        session.add(player)
        return player