from redbot.core import commands
from discord import Embed
from datetime import datetime
import requests


class CurrencyExchange(commands.Cog):
    """Basic currency conversion cog"""

    def __init__(self, bot):
        self.bot = bot
        self._url = 'https://currencyapi.net/api/v1/rates'
        self._refresh_interval = 6  # in hours
        self.rate_data = {}

    @commands.command()
    async def currex(self, ctx: commands.Context, from_currency: str, to_currency: str, amount: float=1):
        """Convert currency"""
        if len(from_currency) != 3:
            return await ctx.send("Invalid 'from' currency")
        if len(to_currency) != 3:
            return await ctx.send("Invalid 'to' currency")
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        key = await self.bot.get_shared_api_tokens("currencyapi")
        if key.get("api_key") is None:
            return await ctx.send("api_key has not been set.")

        p = {
            'key': key.get("api_key"),
            'base': 'USD',
            'output': 'JSON'
        }

        if self.rate_data:
            delta = datetime.now() - datetime.fromtimestamp(self.rate_data['updated'])
            if delta.seconds > self._refresh_interval * 3600:
                self.rate_data = requests.get(self._url, params=p).json()
        else:
            self.rate_data = requests.get(self._url, params=p).json()

        if self.rate_data['valid']:
            try:
                converted = (self.rate_data['rates'][to_currency] / self.rate_data['rates'][from_currency])
                converted *= amount
                converted = round(converted, 3)
            except Exception as e:
                return await ctx.send(f'{e} Invalid currency')

            await ctx.send(embed=Embed(
                title = f'{amount} **{from_currency}**  =  {converted} **{to_currency}**',
                description = f"Updated {datetime.utcfromtimestamp(self.rate_data['updated']).strftime('%B %d %H:%M')} UTC",
                colour = await ctx.embed_colour()
            ))
        else:
            return await ctx.send(f"Invalid request: {self.rate_data['error']['message']}")