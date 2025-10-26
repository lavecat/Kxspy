import kxspy
import discord
from discord import app_commands
from kxspy.events import *
from discord.ext import commands

class cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        bot.kxs = kxspy.Client(
            ws_url="wss://network.kxs.rip/",
            username="Username",
            enablevoicechat=False,
            exchangekey="your_exchange_key_here",
            connect=True # Connect automatically or false to mannualy
        )
        self.kxs: kxspy.client.Client = bot.kxs
        self.kxs.add_event_hooks(self)
        self.game_id = None

    def cog_unload(self):
        """
        This will remove any registered event hooks when the cog is unloaded.
        They will subsequently be registered again once the cog is loaded.

        This effectively allows for event handlers to be updated when the cog is reloaded.
        """
        self.kxs.remove_event_hooks(self)

    async def cog_load(self):
        print("Cog loading...")
        #await self.kxspy.connect() Connect mannualy if connect=False

    async def cog_app_command_error(self, interaction, error):
        if isinstance(error, app_commands.CommandInvokeError):
            await interaction.response.send_message(error.original)

    @kxspy.listener(IdentifyEvent)
    async def Identify(self, event: IdentifyEvent):
        print(event)
        print("KxsNetwork is connected successfully!")

    @kxspy.listener(ExchangejoinEvent)
    async def JoinEvent(self, event: ExchangejoinEvent):
        await self.kxs.join_game(event.gameId)
        self.game_id = event.gameId
        print("The bot join the game successfully!")

    @kxspy.listener(ExchangeGameEnd)
    async def GameEnd(self, event: ExchangeGameEnd):
        self.game_id = None
        await self.kxs.leave_game()

    @kxspy.listener(ChatMessage)
    async def ChatMessage(self, event: ChatMessage):
        if event.text == "!ping":
            await self.kxs.send_message("Pong !")

    @kxspy.listener(ErrorEvent)
    async def Error(self, event: ErrorEvent):
        print(f"ErrorEvent: {event.error} event : {event.event}")

    @app_commands.command(name="send_message", description="Send a message in the current game")
    async def send_msg(self,message: str, interaction: discord.Interaction):
        """Send a message in the current game."""
        await interaction.response.defer(ephemeral=False)

        if self.game_id is None:
            await interaction.followup.send("The bot is not in a game")
            return

        await self.kxs.send_message(message)
        await interaction.followup.send("Message sent to Kxs Network!")

async def setup(bot):
    await bot.add_cog(cog(bot))

