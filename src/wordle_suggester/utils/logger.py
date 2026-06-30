import functools
import logging

import discord

def log_command(logger: logging.Logger):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, ctx: discord.ApplicationContext, *args, **kwargs):
            logger.info(f"In ({ctx.guild}:{ctx.channel}) user {ctx.author} ({ctx.author.id}) used /{ctx.command.name} with {kwargs}")
            return await func(self, ctx, *args, **kwargs)
        return wrapper
    return decorator