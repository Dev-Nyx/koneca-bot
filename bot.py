import discord
import os
import traceback
from db.database import init_db
import db.models
import asyncio
import re
from datetime import datetime, timezone, timedelta
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot online como {bot.user}")
    await init_db()


@bot.event
async def on_message(message):

    if message.author.bot:
        return

    bot_channel_id = int(os.getenv("BOT_CHANNEL_ID"))

    # ignora mensagens do canal do bot para evitar loop
    if message.channel.id == bot_channel_id:
        await bot.process_commands(message)
        return

    # busca padrão [NomePersonagem]
    match = re.search(r"\[(.+?)\]", message.content)

    if match:
        nome = match.group(1).strip()
        print(f"PERSONAGEM DETECTADO: {nome}")

        from db.database import AsyncSessionLocal
        from services.player_service import PlayerService
        from services.character_service import CharacterService

        async with AsyncSessionLocal() as session:

            player = await PlayerService.get_by_discord_id(
                session, str(message.author.id)
            )

            if not player:
                print(" NÃO ENCONTRADA NO BANCO")
                await bot.process_commands(message)
                return

            char = await CharacterService.get_by_name(
                session, player.id, nome
            )

            if not char:
                print(f"Personagem {nome} não encontrado no banco")
                await bot.process_commands(message)
                return

            if not char.done:
                try:
            
                    await CharacterService.mark_done(session, char)

                    notify_channel_id = int(os.getenv("NOTIFY_CHANNEL_ID"))
                    await CharacterService.handle_partner_loop(
                        session, char, bot, notify_channel_id
                    )

                    await session.commit()

                    bot_channel = bot.get_channel(bot_channel_id)
                    BRT = timezone(timedelta(hours=-3))
                    agora = datetime.now(BRT).strftime("%d/%m/%Y %H:%M")        

                    if bot_channel:
                        await bot_channel.send(
                            f"✅ **{char.name}** concluído por {message.author.mention} em {agora}"
                        )
                except Exception as e:
                    print(f"ERRO NO ON_MESSAGE: {e}")
                    traceback.print_exc()

        await bot.process_commands(message)

async def main():
    async with bot:
        await bot.load_extension("cogs.admin")
        await bot.start(os.getenv("DISCORD_TOKEN"))

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Bot desligado com segurança")
except Exception as e:
    print("Erro ao iniciar o bot:")
    traceback.print_exc()