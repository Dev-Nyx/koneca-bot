#  🐱 Koneca Bot

Bot de Discord para gerenciamento de sessões de RPG. Rastreia personagens, registra turnos concluídos e notifica automaticamente o próximo jogador quando é a vez dele.

## Funcionalidades

- Detecção automática de personagens via padrão `[NomePersonagem]` nas mensagens
- Loop de turnos entre pares — quando um personagem é marcado como feito, o par é resetado e a jogadora é notificada automaticamente
- Cadastro de múltiplos personagens por jogadora (separados por vírgula)
- Vínculo e desvínculo de pares entre personagens
- Sorteio aleatório de personagem pendente
- Controle de acesso por cargo (Mestre / Mago)
- Comandos apagados automaticamente após resposta para manter o canal limpo

## Comandos

### Jogadores

| Comando | Descrição |
|---|---|
| `!lista` | Lista seus personagens pendentes e concluídos |
| `!feito <nome>` | Marca um personagem como concluído manualmente |
| `!resetar <nome>` | Volta um personagem para pendente |
| `!sortear` | Sorteia um personagem pendente aleatoriamente |
| `!pares` | Lista seus personagens vinculados e seus pares |

### Mestre (acesso restrito)

| Comando | Descrição |
|---|---|
| `!add_membro @usuario` | Cadastra no sistema |
| `!add_persona "Nome1, Nome2" @usuario` | Cadastra um ou mais personagens para um jogador |
| `!deletar <nome>` | Remove um personagem |
| `!vincular "NomeA" "NomeB"` | Vincula dois personagens como par |
| `!desvincular "Nome"` | Remove o vínculo de par de um personagem |
| `!par-geral` | Lista todos os pares vinculados no servidor |

## Stack

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.10+ |
| Discord | discord.py 2.4.0 |
| ORM | SQLAlchemy 2.0 (assíncrono) |
| Banco de dados | PostgreSQL 14 |
| Driver async | asyncpg 0.31.0 |
| Configuração | python-dotenv |
| Infraestrutura | Oracle Cloud VM — Ubuntu 22.04 |
| Containerização | Docker + Docker Compose (em progresso) |

## Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
DISCORD_TOKEN=token_do_bot
BOT_CHANNEL_ID=id_do_canal_do_bot
NOTIFY_CHANNEL_ID=id_do_canal_de_notificacoes
ROLE_MESTRE=id_do_cargo_mestre
ROLE_MAGO=id_do_cargo_mago
DATABASE_URL=postgresql+asyncpg://usuario:senha@localhost/nome_do_banco
```

## Como Rodar Localmente

**Requisitos:** Python 3.10+, PostgreSQL 14+

```bash
# clonar o repositório
git clone https://github.com/Dev-Nyx/koneca-bot.git
cd koneca-bot

# criar e ativar o ambiente virtual
python3 -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows

# instalar dependências
pip install -r requirements.txt

# configurar variáveis de ambiente
cp .env.example .env
# editar o .env com seus valores

# iniciar o bot
python3 bot.py
```

## Notas Técnicas

- O banco utiliza `DateTime(timezone=True)` em todas as colunas de data para compatibilidade com PostgreSQL e datetimes timezone-aware do Python
- As sequences do PostgreSQL (`players_id_seq`, `characters_id_seq`) precisam de permissão explícita de `USAGE`, `SELECT` e `UPDATE` para o usuário do banco
- O padrão de detecção de turno usa regex `\[(.+?)\]` nas mensagens — personagens com colchetes no nome são detectados automaticamente
