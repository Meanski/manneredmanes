import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import json
import os

class SupportTicket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tickets_file = 'tickets.json'
        self.tickets = self.load_tickets()
        self.category_id = 1256359610604847266  # Replace with your category ID

    def save_tickets(self):
        with open(self.tickets_file, 'w') as f:
            json.dump(self.tickets, f, indent=4)

    def load_tickets(self):
        if os.path.exists(self.tickets_file):
            with open(self.tickets_file, 'r') as f:
                return json.load(f)
        return {}

    @app_commands.command(name="createticket", description="Creates a support ticket.")
    async def create_ticket(self, interaction: discord.Interaction, issue: str):
        """Creates a support ticket."""
        guild = interaction.guild
        author = interaction.user
        category = discord.utils.get(guild.categories, id=self.category_id)

        if not category:
            await interaction.response.send_message(f"Category with ID {self.category_id} not found.", ephemeral=True)
            return

        # Check if user already has an open ticket
        for ticket_info in self.tickets.values():
            if ticket_info['author'] == author.id and ticket_info['status'] == 'open':
                await interaction.response.send_message(f"{author.mention}, you already have an open ticket.", ephemeral=True)
                return

        # Create a new channel for the ticket in the specified category
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            author: discord.PermissionOverwrite(read_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }

        ticket_channel = await category.create_text_channel(
            name=f'ticket-{author.name}',
            overwrites=overwrites
        )

        self.tickets[str(ticket_channel.id)] = {
            'author': author.id,
            'issue': issue,
            'status': 'open'
        }
        self.save_tickets()

        embed = discord.Embed(
            title="New Support Ticket",
            description=f"**Issue:** {issue}\n**Status:** Open",
            color=discord.Color.blue()
        )
        embed.set_author(name=author.display_name, icon_url=author.avatar.url)
        embed.set_footer(text="To close this ticket, please use the /closeticket command")
        await ticket_channel.send(embed=embed)

        await interaction.response.send_message(f"{author.mention}, your ticket has been created: {ticket_channel.mention}", ephemeral=True)

    @app_commands.command(name="closeticket", description="Initiates closing the support ticket.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def close_ticket(self, interaction: discord.Interaction):
        """Initiates closing the support ticket."""
        channel = interaction.channel

        if str(channel.id) in self.tickets:
            ticket_info = self.tickets[str(channel.id)]
            if ticket_info['status'] == 'closed':
                await interaction.response.send_message("This ticket is already closed.", ephemeral=True)
                return

            await interaction.response.defer(ephemeral=True)

            embed = discord.Embed(
                title="Ticket Closure Confirmation",
                description="React with ✅ to confirm closure or ❌ to cancel.",
                color=discord.Color.orange()
            )
            message = await channel.send(embed=embed)
            await message.add_reaction("✅")
            await message.add_reaction("❌")

            def check(reaction, user):
                return user == interaction.user and str(reaction.emoji) in ["✅", "❌"]

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=600.0, check=check)  # 10 minutes timeout

                if str(reaction.emoji) == "✅":
                    await self.send_survey(channel, ticket_info, interaction.user)
                else:
                    await interaction.followup.send("Ticket closure cancelled.", ephemeral=True)
            except asyncio.TimeoutError:
                await interaction.followup.send("Ticket closure timed out.", ephemeral=True)
        else:
            await interaction.response.send_message("This channel is not a support ticket.", ephemeral=True)

    async def send_survey(self, channel, ticket_info, user):
        """Send survey and handle rating."""
        ticket_info['status'] = 'closed'
        self.save_tickets()

        # Post survey rating
        survey_embed = discord.Embed(
            title="Rate Your Experience",
            description="Please rate your support experience, with 5 being the best. This channel will automatically close in 5 minutes.",
            color=discord.Color.green()
        )
        survey_message = await channel.send(embed=survey_embed)
        for i in range(1, 6):
            await survey_message.add_reaction(str(i) + "\u20E3")  # Number emojis 1️⃣, 2️⃣, etc.

        def survey_check(reaction, survey_user):
            return survey_user == user and str(reaction.emoji) in [str(i) + "\u20E3" for i in range(1, 6)]

        try:
            reaction, survey_user = await self.bot.wait_for('reaction_add', timeout=300.0, check=survey_check)  # 5 minutes timeout
            rating = str(reaction.emoji)[0]
            ticket_info['rating'] = int(rating)
            self.save_tickets()
            await channel.send(f"Thank you for rating your experience as {rating}/5.")
        except asyncio.TimeoutError:
            await channel.send("Rating timed out. No rating recorded.")

        # Send closure embed and close the channel
        close_embed = discord.Embed(
            title="Ticket Closed",
            description=f"**Issue:** {ticket_info['issue']}\n**Status:** Closed",
            color=discord.Color.red()
        )
        await channel.send(embed=close_embed)
        await asyncio.sleep(10)  # Wait for 10 seconds before deleting the channel
        await channel.delete()

    @close_ticket.error
    async def close_ticket_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("You do not have permission to close tickets.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SupportTicket(bot))

    # Register commands only if not already registered
    if not bot.tree.get_command("createticket"):
        bot.tree.add_command(SupportTicket.create_ticket)
    if not bot.tree.get_command("closeticket"):
        bot.tree.add_command(SupportTicket.close_ticket)

async def teardown(bot):
    # Unregister commands when the cog is unloaded
    if bot.tree.get_command("createticket"):
        bot.tree.remove_command(SupportTicket.create_ticket.name)
    if bot.tree.get_command("closeticket"):
        bot.tree.remove_command(SupportTicket.close_ticket.name)
