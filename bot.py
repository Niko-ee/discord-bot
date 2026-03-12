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