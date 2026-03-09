import discord
import os
import random
import asyncio
import aiohttp
import html
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    guild = discord.Object(id=1480516340270891028)  # Replace with your server ID
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
    print(f"Logged in as {bot.user}")

# /embed command
@bot.tree.command(name="embed", description="Send a fancy embed")
async def embed(interaction: discord.Interaction, title: str, message: str):
    e = discord.Embed(title=title, description=message, color=0x5865F2)
    e.set_footer(text=f"Requested by {interaction.user}")
    await interaction.response.send_message(embed=e)

# /coinflip command
@bot.tree.command(name="coinflip", description="Flip a coin!")
async def coinflip(interaction: discord.Interaction):
    result = random.choice(["Heads 🪙", "Tails 🪙"])
    e = discord.Embed(title="Coin Flip!", description=f"It landed on **{result}**!", color=0xFFD700)
    await interaction.response.send_message(embed=e)

# /8ball command
@bot.tree.command(name="8ball", description="Ask the magic 8ball a question")
async def eightball(interaction: discord.Interaction, question: str):
    responses = [
        "It is certain ✅", "Without a doubt ✅", "Yes definitely ✅",
        "Most likely ✅", "Signs point to yes ✅", "Reply hazy, try again 🤔",
        "Ask again later 🤔", "Cannot predict now 🤔", "Don't count on it ❌",
        "My sources say no ❌", "Outlook not so good ❌", "Very doubtful ❌"
    ]
    e = discord.Embed(title="🎱 Magic 8Ball", color=0x36393F)
    e.add_field(name="Question", value=question, inline=False)
    e.add_field(name="Answer", value=random.choice(responses), inline=False)
    await interaction.response.send_message(embed=e)

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

# /roll command
@bot.tree.command(name="roll", description="Roll a dice")
async def roll(interaction: discord.Interaction, sides: int = 6):
    result = random.randint(1, sides)
    await interaction.response.send_message(f"🎲 You rolled a **{result}** (d{sides})")

# /trivia command
@bot.tree.command(name="trivia", description="Get a random trivia question!")
async def trivia(interaction: discord.Interaction):
    await interaction.response.defer()
    async with aiohttp.ClientSession() as session:
        async with session.get("https://opentdb.com/api.php?amount=1&type=multiple") as resp:
            data = await resp.json()

    q = data["results"][0]
    question = html.unescape(q["question"])
    correct = html.unescape(q["correct_answer"])
    wrong = [html.unescape(a) for a in q["incorrect_answers"]]
    options = wrong + [correct]
    random.shuffle(options)

    options_text = "\n".join([f"{i+1}. {o}" for i, o in enumerate(options)])
    correct_num = options.index(correct) + 1

    e = discord.Embed(title="🧠 Trivia Time!", color=0x9B59B6)
    e.add_field(name="Category", value=q["category"], inline=True)
    e.add_field(name="Difficulty", value=q["difficulty"].capitalize(), inline=True)
    e.add_field(name=question, value=options_text, inline=False)
    e.set_footer(text=f"The answer is number {correct_num} — revealed in 10 seconds!")
    msg = await interaction.followup.send(embed=e)
    await asyncio.sleep(10)
    e.set_footer(text=f"✅ The answer was: {correct}")
    await msg.edit(embed=e)

# /kick command
@bot.tree.command(name="kick", description="Kick a member")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    await interaction.response.defer(ephemeral=True)
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

@kick.error
async def kick_error(interaction: discord.Interaction, error):
    await interaction.followup.send("❌ You don't have permission to kick members!")

bot.run(os.getenv("TOKEN"))