import discord
import os
from dotenv import load_dotenv

load_dotenv()
ROLE_MESTRE = int(os.getenv("ROLE_MESTRE"))
ROLE_MAGO = int(os.getenv("ROLE_MAGO"))

def is_mestre(member: discord.Member):
    return any(role.id == ROLE_MESTRE for role in member.roles)

def is_mago(member: discord.Member):
    return any(role.id == ROLE_MAGO for role in member.roles)

def pode_cadastrar_personagem(member: discord.Member):
    return is_mestre(member) or is_mago(member)