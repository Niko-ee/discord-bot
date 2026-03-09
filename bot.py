import discord
import os
import random
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    guild = discord.Object(id=1480516340270891028)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
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

bot.run(os.getenv("TOKEN"))