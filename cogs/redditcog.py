import discord
from discord import app_commands
from discord.ext import commands, tasks

import asyncprawcore

import time

from util.general import *
from util.redditfetch import RedditPost, new_reddit_posts, reddit
from util.const import redditfollows, savejson
from util.webhookhelper import get_webhook
from util.telegramhelper import tg_send


class RedditCog(commands.GroupCog, group_name='reddit'):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.reddit_parse_all.start()
        print("Loaded", __class__.__name__)

    # fetching job
    @tasks.loop(hours=1)
    async def reddit_parse_all(self):
        print("Parsing reddit")
        after = redditfollows["last"]
        before = time.time()
        for subreddit in redditfollows["subs"]:
            async for submission in new_reddit_posts(subreddit, after, before):
                await submission.load()
                post = RedditPost(submission.shortlink)
                await post.generate(submission)

                # telegram
                for chat_id in redditfollows["subs"][subreddit]["tg"]:
                    try:
                        await tg_send(chat_id, post)
                    except Exception as e:
                        print(f"Error sending to telegram: {e}")
                
                # discord
                for channel_id in redditfollows["subs"][subreddit]["dc"]:
                    try:
                        webhook = await get_webhook(channel_id, self.bot)
                        await webhook.send(post.webhook_message(), username=post.webhook_username(), avatar_url=post.webhook_avatar())
                    except Exception as e:
                        print(f"Error sending to discord: {e}")
        
        redditfollows["last"] = before
        savejson("conf/redditfollows", redditfollows)

    @reddit_parse_all.before_loop
    async def _before_loop(self):
        await self.bot.wait_until_ready()
                

    @app_commands.command(name="follow", description="follows a subreddit")
    async def reddit_follow(self, interaction: discord.Interaction, subreddit: str):
        if not await devcheck(interaction):
            return
        
        await interaction.response.defer(ephemeral=False)

        try:
            if subreddit.startswith("r/"):
                subreddit = subreddit[2:]

            sub = await reddit.subreddit(subreddit, fetch=True)
            subreddit = sub.display_name
            
            # make key if it doesnt exist
            if subreddit not in redditfollows["subs"]:
                redditfollows["subs"][subreddit] = {"dc": [], "tg": []}
            # check if already following
            if interaction.channel_id not in redditfollows["subs"][subreddit]["dc"]:
                redditfollows["subs"][subreddit]["dc"].append(interaction.channel_id)
            # save changes
            savejson("conf/redditfollows", redditfollows)
            
            await interaction.followup.send(f"Followed {subreddit}")
        
        except asyncprawcore.exceptions.Redirect as e:
            await interaction.followup.send(embed=errorembed(f"Couldnt find subreddit"))
            return

        except Exception as e:
            await interaction.followup.send(embed=errorembed(f"Error: {e}"))
            return
        
    
    @app_commands.command(name="unfollow", description="unfollows a subreddit")
    async def reddit_unfollow(self, interaction: discord.Interaction, subreddit: str):
        if not await devcheck(interaction):
            return
        
        await interaction.response.defer(ephemeral=False)

        try:
            if subreddit.startswith("r/"):
                subreddit = subreddit[2:]

            sub = await reddit.subreddit(subreddit, fetch=True)
            subreddit = sub.display_name

            # if the key exists
            if subreddit in redditfollows["subs"]:
                # remove channel
                redditfollows["subs"][subreddit]["dc"].remove(interaction.channel_id)
                # remove empty keys
                if redditfollows["subs"][subreddit] == {"dc": [], "tg": []}:
                    del redditfollows["subs"][subreddit]
                # save changes
                savejson("conf/redditfollows", redditfollows)
            
            await interaction.followup.send(f"Unollowed {subreddit}")
        
        except asyncprawcore.exceptions.Redirect as e:
            await interaction.followup.send(embed=errorembed(f"Couldnt find subreddit"))
            return

        except Exception as e:
            await interaction.followup.send(embed=errorembed(f"Error: {e}"))
            return

        


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RedditCog(bot))