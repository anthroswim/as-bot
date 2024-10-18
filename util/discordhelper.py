import discord
# TODO: make cache expire
webhook_cache = {}

async def get_webhook(channel, bot = None) -> discord.Webhook:
    if channel.id in webhook_cache:
        return webhook_cache[channel.id]
    
    if not bot:
        return None
    
    webhooks = await channel.webhooks()

    # check if theres a valid webhook already we can use
    for webhook in webhooks:
        if webhook.name == "ASFeed":
            webhook_cache[channel.id] = webhook
            return webhook
    else:
        webhook = await channel.create_webhook(name="ASFeed")
        webhooks = await channel.webhooks()
        webhook_cache[channel.id] = webhook
        return webhook
    
async def discord_post(channel, bot, post):
    # kwargs magic
    kwargs = {
        "username": post.get_username(),
        "avatar_url": post.get_avatar()
    }
    
    if files := post.get_files():
        kwargs["files"] = [discord.File(f) for f in files]
    
    if isinstance(channel, discord.Thread):
        kwargs["thread"] = channel
        channel = channel.parent
    
    webhook = await get_webhook(channel, bot)

    try:
        message = post.get_message(include_author=False, include_medialinks=not files)
        await webhook.send(message, **kwargs)
    except Exception as e:
        print(f"Error sending to discord: {e}")
        # retry without files
        message = post.get_message(include_author=False, include_medialinks=True)
        kwargs.pop("files")
        await webhook.send(message, **kwargs)
