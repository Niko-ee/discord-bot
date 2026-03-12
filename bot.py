import os
import random
import discord
from groq import AsyncGroq
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

# /embed command
@bot.tree.command(name="embed", description="Send a fancy embed")
async def embed(interaction: discord.Interaction, title: str, message: str):
    e = discord.Embed(title=title, description=message, color=0x5865F2)
    e.set_footer(text=f"Requested by {interaction.user}")
    await interaction.response.send_message(embed=e)

# /roll command
@bot.tree.command(name="roll", description="Roll a dice")
async def roll(interaction: discord.Interaction, sides: int = 6):
    result = random.randint(1, sides)
    await interaction.response.send_message(f"🎲 You rolled a **{result}** (d{sides})")

# /kick command
@bot.tree.command(name="kick", description="Kick a member")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    await interaction.response.defer(ephemeral=True)
    allowed_role_id = 1323031720609714309
    user_role_ids = [role.id for role in interaction.user.roles]
    if allowed_role_id not in user_role_ids:
        await interaction.followup.send("❌ You don't have permission to use this command!")
        return
    if member == interaction.user:
        await interaction.followup.send("❌ You can't kick yourself!")
        return
    if member.top_role >= interaction.guild.me.top_role:
        await interaction.followup.send("❌ That person's role is higher than mine, I can't kick them!")
        return
    await member.kick(reason=reason)
    e = discord.Embed(title="✅ Member Kicked", color=0xFF0000)
    e.add_field(name="User", value=member.mention)
    e.add_field(name="Reason", value=reason)
    e.add_field(name="Moderator", value=interaction.user.mention)
    await interaction.followup.send(embed=e)

# /rps command
@bot.tree.command(name="rps", description="Play rock paper scissors against the bot!")
@app_commands.choices(choice=[
    app_commands.Choice(name="Rock 🪨", value="rock"),
    app_commands.Choice(name="Paper 📄", value="paper"),
    app_commands.Choice(name="Scissors ✂️", value="scissors"),
])
async def rps(interaction: discord.Interaction, choice: app_commands.Choice[str]):
    bot_choice = random.choice(["rock", "paper", "scissors"])
    emojis = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
    wins = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
    if choice.value == bot_choice:
        result = "It's a tie! 🤝"
        color = 0xFFFF00
    elif wins[choice.value] == bot_choice:
        result = "You win! 🎉"
        color = 0x00FF00
    else:
        result = "You lose! 💀"
        color = 0xFF0000
    e = discord.Embed(title="Rock Paper Scissors!", color=color)
    e.add_field(name="Your choice", value=emojis[choice.value])
    e.add_field(name="Bot's choice", value=emojis[bot_choice])
    e.add_field(name="Result", value=result, inline=False)
    await interaction.response.send_message(embed=e)

# /ping command
@bot.tree.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.Interaction):
    latency_ms = round(bot.latency * 1000)
    await interaction.response.send_message(f"🛰️ Pong! **{latency_ms}ms**")

# /coinflip command
@bot.tree.command(name="coinflip", description="Flip a coin")
async def coinflip(interaction: discord.Interaction):
    result = random.choice(["Heads", "Tails"])
    await interaction.response.send_message(f"🪙 **{result}**")

# /say command
@bot.tree.command(name="say", description="Make the bot say something")
async def say(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)

# /serverinfo command
@bot.tree.command(name="serverinfo", description="Show info about this server")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return
    e = discord.Embed(title=guild.name, color=0x5865F2)
    e.add_field(name="Members", value=str(guild.member_count))
    e.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown")
    e.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"))
    if guild.icon:
        e.set_thumbnail(url=guild.icon.url)
    await interaction.response.send_message(embed=e)

# /userinfo command
@bot.tree.command(name="userinfo", description="Show info about a user")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    e = discord.Embed(title=str(member), color=0x5865F2)
    e.add_field(name="ID", value=str(member.id))
    e.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d") if member.joined_at else "Unknown")
    e.add_field(name="Account created", value=member.created_at.strftime("%Y-%m-%d"))
    e.set_thumbnail(url=member.display_avatar.url)
    await interaction.response.send_message(embed=e)

# /ai command
@bot.tree.command(name="ai", description="Ask AI anything!")
async def ai(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    try:
        response = await groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful assistant in a Discord server. Keep responses concise and friendly."},
                {"role": "user", "content": question}
            ],
            max_tokens=500
        )
        answer = response.choices[0].message.content
        if len(answer) > 4096:
            answer = answer[:4093] + "..."
        e = discord.Embed(title="🤖 AI Response", description=answer, color=0x00BFFF)
        e.add_field(name="Question", value=question, inline=False)
        e.set_footer(text=f"Asked by {interaction.user} • Powered by Llama 3")
        await interaction.followup.send(embed=e)
    except Exception as ex:
        await interaction.followup.send(f"❌ Something went wrong: {ex}")

        # /tictactoe command
class TicTacToeButton(discord.ui.Button):
    def __init__(self, x, y):
        super().__init__(style=discord.ButtonStyle.secondary, label="​", row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        view: TicTacToeView = self.view
        if interaction.user != view.current_player:
            await interaction.response.send_message("❌ It's not your turn!", ephemeral=True)
            return
        if view.board[self.y][self.x] != 0:
            await interaction.response.send_message("❌ That spot is already taken!", ephemeral=True)
            return

        if view.current_player == view.player1:
            self.label = "❌"
            self.style = discord.ButtonStyle.danger
            view.board[self.y][self.x] = 1
            view.current_player = view.player2
        else:
            self.label = "⭕"
            self.style = discord.ButtonStyle.success
            view.board[self.y][self.x] = 2
            view.current_player = view.player1

        self.disabled = True
        winner = view.check_winner()

        if winner:
            for child in view.children:
                child.disabled = True
            if winner == "tie":
                await interaction.response.edit_message(content="It's a tie! 🤝", view=view)
            else:
                await interaction.response.edit_message(content=f"🎉 {winner.mention} wins!", view=view)
        else:
            await interaction.response.edit_message(content=f"It's {view.current_player.mention}'s turn!", view=view)

class TicTacToeView(discord.ui.View):
    def __init__(self, player1, player2):
        super().__init__()
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        for y in range(3):
            for x in range(3):
                self.add_item(TicTacToeButton(x, y))

    def check_winner(self):
        b = self.board
        for i in range(3):
            if b[i][0] == b[i][1] == b[i][2] != 0:
                return self.player1 if b[i][0] == 1 else self.player2
            if b[0][i] == b[1][i] == b[2][i] != 0:
                return self.player1 if b[0][i] == 1 else self.player2
        if b[0][0] == b[1][1] == b[2][2] != 0:
            return self.player1 if b[0][0] == 1 else self.player2
        if b[0][2] == b[1][1] == b[2][0] != 0:
            return self.player1 if b[0][2] == 1 else self.player2
        if all(b[y][x] != 0 for y in range(3) for x in range(3)):
            return "tie"
        return None

@bot.tree.command(name="tictactoe", description="Play tictactoe against another player!")
async def tictactoe(interaction: discord.Interaction, opponent: discord.Member):
    if opponent == interaction.user:
        await interaction.response.send_message("❌ You can't play against yourself!", ephemeral=True)
        return
    if opponent.bot:
        await interaction.response.send_message("❌ You can't play against a bot!", ephemeral=True)
        return
    view = TicTacToeView(interaction.user, opponent)
    await interaction.response.send_message(
        content=f"⚔️ {interaction.user.mention} ❌ vs {opponent.mention} ⭕\nIt's {interaction.user.mention}'s turn!",
        view=view
    )

bot.run(os.getenv("TOKEN"))