# TODO: make cache expire
webhook_cache = {}

async def get_webhook(ch_id: int, bot = None):
    if ch_id in webhook_cache:
        return webhook_cache[ch_id]
    
    if not bot:
        return None
    
    channel = bot.get_channel(ch_id)
    webhooks = await channel.webhooks()
    if not webhooks:
        await channel.create_webhook(name="FeedHelper")
        webhooks = await channel.webhooks()
    
    webhook_cache[ch_id] = webhooks[0]
    return webhooks[0]