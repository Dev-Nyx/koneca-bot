from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base
from sqlalchemy import UniqueConstraint
from datetime import datetime, timezone


# cada jogadora que participa do RPG
class Player(Base):

    __tablename__ = "players"
    id = Column(Integer, primary_key=True)
    discord_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # lista de personagens da jogadora
    characters = relationship(
        "Character",
        back_populates="player",
        cascade="all, delete"
    )

    def __repr__(self):
        return f"<Player {self.name}>"

# cada personagem cadastrado no rpg
class Character(Base):

    __tablename__ = "characters"

    __table_args__ = (
    UniqueConstraint('name', 'player_id', name='uq_character_player'),
)

   
    id = Column(Integer, primary_key=True)  
    name = Column(String, nullable=False, index=True)
    done = Column(Boolean, default=False)
    done_at = Column(DateTime, nullable=True)

    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    partner_id = Column(Integer, ForeignKey("characters.id"), nullable=True)

    # relacionamento de volta para a jogadora
    player = relationship(
        "Player",
       back_populates="characters"
    )

    partner = relationship(
        "Character",
        foreign_keys=[partner_id],
        uselist=False
    )

    def __repr__(self):
        status = "✅" if self.done else "⏳"
        return f"<Character {status} {self.name}>"
    
    