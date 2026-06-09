from discord.ext import commands
from db.models import Character, Player
from sqlalchemy import func, select
import discord
from db.database import AsyncSessionLocal
from services.player_service import PlayerService
from services.character_service import CharacterService
from utils.permissions import is_mestre, pode_cadastrar_personagem
import random



class AdminCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # lista - mostra a lista de personagens por jogadora
    @commands.command(name="lista")
    async def lista(self, ctx):

        async with AsyncSessionLocal() as session:

            player = await PlayerService.get_by_discord_id(
                session, str(ctx.author.id)
            )

            if not player:
                await ctx.send("⚠️ Você não está cadastrada.")
                return

            chars = await CharacterService.list_all(session, player.id)

            if not chars:
                await ctx.send("📭 Você não tem personagens.")
                return

            pendentes = [c.name for c in chars if not c.done]
            feitos = [c.name for c in chars if c.done]

            embed = discord.Embed(
                title=f"📜 Personagens de {ctx.author.display_name}",
                color=discord.Color.blue()
            )

            if pendentes:
                embed.add_field(
                    name="⏳ Pendentes",
                    value=", ".join(pendentes),
                    inline=False
                )

            if feitos:
                embed.add_field(
                    name="✅ Concluídos",
                    value=", ".join(feitos),
                    inline=False
                )

            await ctx.send(embed=embed)
            # Apaga o comando após responder, deixa o canal limpo
            await ctx.message.delete()

   
    # feito - marca o personagem como feito
    @commands.command(name="feito")
    async def feito(self, ctx, *, name: str):

        async with AsyncSessionLocal() as session:

            player = await PlayerService.get_by_discord_id(
                session, str(ctx.author.id)
            )

            if not player:
                await ctx.send("⚠️ Você não está cadastrada.")
                return

            char = await CharacterService.get_by_name(
                session, player.id, name
            )

            if not char:
                await ctx.send("❌ Personagem não encontrado.")
                return

            if char.done:
                await ctx.send("⚠️ Já estava marcado como feito.")
                return

            await CharacterService.mark_done(session, char)
            await session.commit()

            await ctx.send(f"✅ {char.name} marcado como concluído!")
            await ctx.message.delete()



   # sortea um personagem aleátorio 
    @commands.command(name="sortear")
    async def proximo(self, ctx):

        async with AsyncSessionLocal() as session:

            player = await PlayerService.get_by_discord_id(
                session, str(ctx.author.id)
            )

            if not player:
                await ctx.send("⚠️ Você não está cadastrada.")
                return

            pendentes = await CharacterService.list_pending(
                session, player.id
            )

            if not pendentes:
                await ctx.send("🎉 Você não tem pendências!")
                return

            escolhido = random.choice(pendentes)

            await ctx.send(
                f"🎲 O destino escolheu...\n"
                f"✨ **{escolhido.name}**"
            )
            # Apaga o comando após responder — deixa o canal limpo
            await ctx.message.delete()

    # reseta o personagem para pendencia
    @commands.command(name="resetar")
    async def reset(self, ctx, *, name: str):

        async with AsyncSessionLocal() as session:

            player = await PlayerService.get_by_discord_id(
                session, str(ctx.author.id)
            )

            if not player:
                await ctx.send("⚠️ Você não está cadastrada.")
                return

            char = await CharacterService.get_by_name(
                session, player.id, name
            )

            if not char:
                await ctx.send("❌ Personagem não encontrado.")
                return

            try:
                await CharacterService.reset_done(session, char)
                await session.commit()
                await ctx.send(f"🔄 {char.name} voltou para pendente.")
                await ctx.message.delete()
            except Exception as e:
                print(f"❌ ERRO NO RESETAR: {e}")
                import traceback
                traceback.print_exc()

    # adicionar membro
    @commands.command(name="add_membro")
    async def add_player(self, ctx, member: discord.Member):

        if not is_mestre(ctx.author):
            await ctx.send("❌ Apenas Mestre pode cadastrar membros.")
            return

        async with AsyncSessionLocal() as session:

            player = await PlayerService.get_by_discord_id(
                session, str(member.id)
            )

            if player:
                await ctx.send(f"⚠️ {member.display_name} já está cadastrado!")
                return

            await PlayerService.create_player(session, member)

            await session.commit()

            await ctx.send(f"✅ {member.display_name} cadastrado com sucesso!")
            await ctx.message.delete()

    # deleta personagens
    @commands.command(name="deletar")
    async def delete_char(self, ctx, *, name: str):

        async with AsyncSessionLocal() as session:

            player = await PlayerService.get_by_discord_id(
                session, str(ctx.author.id)
            )

            if not player:
                await ctx.send("⚠️ Você não está cadastrada.")
                return

            char = await CharacterService.get_by_name(
                session, player.id, name
            )

            if not char:
                await ctx.send("❌ Personagem não encontrado.")
                return

            await CharacterService.delete_character(session, char)
            await session.commit()

            await ctx.send(f"🗑️ {char.name} foi removido.")
            await ctx.message.delete()
        
    # adiciona os personagens
    @commands.command(name="add_persona")
    async def add_char(self, ctx, names: str, member: discord.Member):

        if not pode_cadastrar_personagem(ctx.author):
            await ctx.send("❌ Você não tem permissão.")
            return

        # Mago cadastra pra si apenas
        if not is_mestre(ctx.author) and ctx.author != member:
            await ctx.send("❌ Você só pode cadastrar seus próprios personagens.")
            return

        async with AsyncSessionLocal() as session:

            player = await PlayerService.get_by_discord_id(
                session, str(member.id)
            )

            if not player:
                await ctx.send("⚠️ Jogador não cadastrado.")
                return

            cadastrados, duplicados, ignorados = await CharacterService.add_characters(
                session, player, names
            )

            await session.commit()

            embed = discord.Embed(
                title="📜 Resultado do Cadastro",
                color=discord.Color.purple()
            )

            if cadastrados:
                embed.add_field(
                    name="✅ Cadastrados",
                    value=", ".join(cadastrados),
                    inline=False
                )

            if duplicados:
                embed.add_field(
                    name="⚠️ Duplicados",
                    value=", ".join(duplicados),
                    inline=False
                )

            if ignorados:
                embed.add_field(
                    name="🚫 Ignorados",
                    value=", ".join(ignorados),
                    inline=False
                )

            await ctx.send(embed=embed)
            await ctx.message.delete()

   
    # cria o vinculo de par entre dois personagens para os turnos
    # exemplo: !vincular "A" "B"
    @commands.command(name="vincular")
    async def vincular(self, ctx, nome_a: str, nome_b: str):

        if not is_mestre(ctx.author):
            await ctx.send("❌ Apenas o Mestre pode vincular personagens.")
            return

        async with AsyncSessionLocal() as session:

            # busca o personagem A em qualquer jogadora
            result_a = await session.execute(
                select(Character).where(
                    func.lower(func.trim(Character.name)) == nome_a.strip().lower()
                )
            )
            char_a = result_a.scalar_one_or_none()

            # busca o personagem B em qualquer jogadora
            result_b = await session.execute(
                select(Character).where(
                    func.lower(func.trim(Character.name)) == nome_b.strip().lower()
                )
            )
            char_b = result_b.scalar_one_or_none()

            if not char_a:
                await ctx.send(f"❌ Personagem **{nome_a}** não encontrado!")
                return

            if not char_b:
                await ctx.send(f"❌ Personagem **{nome_b}** não encontrado!")
                return

          
            if char_a.partner_id:
                await ctx.send(f"⚠️ **{char_a.name}** já tem um par vinculado! Use !desvincular primeiro.")
                return

            if char_b.partner_id:
                await ctx.send(f"⚠️ **{char_b.name}** já tem um par vinculado! Use !desvincular primeiro.")
                return

            # cria o vinculo entre os dois - aponta um para o outro
            char_a.partner_id = char_b.id
            char_b.partner_id = char_a.id

            await session.commit()

            # BUSCA OS PLAYERS DE FORMA SEGURA (SEM RELATIONSHIP)
            result_players = await session.execute(
                select(Player.id, Player.name).where(
                    Player.id.in_([char_a.player_id, char_b.player_id])
                )
            )

            players = {p.id: p.name for p in result_players.all()}

            player_a_name = players[char_a.player_id]
            player_b_name = players[char_b.player_id]


            await ctx.send(
                f"🔗 Par vinculado com sucesso!\n"
                f"⚔️ **{char_a.name}** ({player_a_name}) ↔️ **{char_b.name}** ({player_b_name})"
            )

            await ctx.message.delete()


    # exemplo: !desvincular "B"
    # Remove o vínculo de par de um personagem
    @commands.command(name="desvincular")
    async def desvincular(self, ctx, nome: str):

        if not is_mestre(ctx.author):
            await ctx.send("❌ Apenas o Mestre pode desvincular personagens.")
            return

        async with AsyncSessionLocal() as session:

            # busca o personagem pelo nome
            result = await session.execute(
                select(Character).where(Character.name.ilike(nome))
            )
            char = result.scalar_one_or_none()

            if not char:
                await ctx.send(f"❌ Personagem **{nome}** não encontrado!")
                return

            if not char.partner_id:
                await ctx.send(f"⚠️ **{char.name}** não tem par vinculado.")
                return

            # busca o par para remover o vinculo dos dois lados
            result_partner = await session.execute(
                select(Character).where(Character.id == char.partner_id)
            )
            partner = result_partner.scalar_one_or_none()

            # remove o vínculo dos dois lados
            char.partner_id = None
            if partner:
                partner.partner_id = None

            await session.commit()

            await ctx.send(f"🔓 Vínculo removido! **{char.name}** está sem par agora.")
            await ctx.message.delete()

    # lista global de pares
    @commands.command(name="par-geral")
    async def pares_all(self, ctx):

        if not is_mestre(ctx.author):
            await ctx.send("❌ Apenas o Mestre pode ver todos os pares.")
            return

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(Character).where(Character.partner_id.is_not(None))
            )

            chars = result.scalars().all()

            if not chars:
                await ctx.send("📭 Nenhum par vinculado.")
                return

            pares_vistos = set()
            lista = []

            for char in chars:
                if char.id in pares_vistos or not char.partner_id:
                    continue

                partner = await session.get(Character, char.partner_id)

                if partner:
                    lista.append(f"💖 {char.name}  ↔  {partner.name}")
                    pares_vistos.add(char.id)
                    pares_vistos.add(partner.id)
                if not lista:
                    await ctx.send("💔 Nenhum casal encontrado.")
                    return
            embed = discord.Embed(
                title="💞 Todos os Casais",
                description="\n".join(lista),
                color=discord.Color.magenta()
            )

            await ctx.send(embed=embed)
            await ctx.message.delete()

    # lista de par da jogadora
    @commands.command(name="pares")
    async def pares(self, ctx):

        async with AsyncSessionLocal() as session:

            player = await PlayerService.get_by_discord_id(
                session, str(ctx.author.id)
            )

            if not player:
                await ctx.send("⚠️ Você não está cadastrada.")
                return

            result = await session.execute(
                select(Character).where(
                    Character.partner_id != None,
                    Character.player_id == player.id
                )
            )

            chars = result.scalars().all()

            if not chars:
                await ctx.send("📭 Você não tem par.")
                return

            pares_vistos = set()
            lista = []

            for char in chars:
                if char.id in pares_vistos:
                    continue

                partner = await session.get(Character, char.partner_id)

                if partner:
                    lista.append(f"❤️‍🔥 {char.name}  ↔  {partner.name}")
                    pares_vistos.add(char.id)
                    pares_vistos.add(partner.id)

            embed = discord.Embed(
                title=f"💞 Casais de {ctx.author.display_name}",
                description="\n".join(lista),
                color=discord.Color.pink()
            )

            await ctx.send(embed=embed)
            await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(AdminCog(bot))