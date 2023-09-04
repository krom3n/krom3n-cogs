from .currency_exchange import CurrencyExchange


async def setup(bot):
    await bot.add_cog(CurrencyExchange(bot))