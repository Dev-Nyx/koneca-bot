from db.models import Character, Player
from sqlalchemy import select, func
from datetime import datetime, timezone


def normalize(name: str):
    return name.strip().lower()


class CharacterService:

    @staticmethod
    async def get_by_name(session, player_id, name: str):
        norm_name = normalize(name)

        result = await session.execute(
        select(Character).where(
            Character.player_id == player_id,
            func.lower(func.trim(Character.name)) == norm_name
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_existing_names(session, player_id):
        result = await session.execute(
            select(Character.name).where(Character.player_id == player_id)
        )
        return {normalize(row[0]) for row in result}

    @staticmethod
    async def add_characters(session, player, raw_names: str):

        name_list = [n.strip() for n in raw_names.split(",") if n.strip()]
        cadastrados = []
        duplicados = []
        ignorados = []

        existing_names = await CharacterService.get_existing_names(session, player.id)

        for name in name_list:
            if len(name) > 50:
                ignorados.append(name)
                continue

            norm = normalize(name)
            if norm in existing_names:
                duplicados.append(name)
                continue

            session.add(Character(
                name=name,
                player_id=player.id,
                done=False
            ))

            cadastrados.append(name)
            existing_names.add(norm)

        return cadastrados, duplicados, ignorados

    @staticmethod
    async def delete_character(session, char):
        await session.delete(char)

    @staticmethod
    async def list_pending(session, player_id):
        result = await session.execute(
            select(Character).where(
                Character.player_id == player_id,
                Character.done == False
            )
        )
        return result.scalars().all()


    @staticmethod
    async def list_all(session, player_id):
        result = await session.execute(
            select(Character).where(
                Character.player_id == player_id
            )
        )
        return result.scalars().all()


    @staticmethod
    async def mark_done(session, character):
        character.done = True
        character.done_at = datetime.now(timezone.utc)


    @staticmethod
    async def reset_done(session, character):
        character.done = False
        character.done_at = None

    @staticmethod
    async def handle_partner_loop(session, char, bot, notify_channel_id: int):
        if not char.partner_id:
            return

        partner = await session.get(Character, char.partner_id)
        if not partner:
            return

        partner_player = await session.get(Player, partner.player_id)
        if not partner_player:
            return

        partner.done = False
        partner.done_at = None

        notify_channel = bot.get_channel(notify_channel_id)
        if notify_channel:
            guild = notify_channel.guild
            member = guild.get_member(int(partner_player.discord_id))
            mention = member.mention if member else partner_player.name
            await notify_channel.send(
                f"🔔 Tá na sua vez {mention} com **{partner.name}**!"
            )        
                  