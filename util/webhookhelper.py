# TODO: make cache expire
webhook_cache = {}

async def get_webhook(ch_id: int, bot = None):
    if ch_id in webhook_cache:
        return webhook_cache[ch_id]
    
    if not bot:
        return None
    
    channel = bot.get_channel(ch_id)
    webhooks = await channel.webhooks()

    # check if theres a valid webhook already we can use
    for webhook in webhooks:
        if webhook.name == "ASFeed":
            webhook_cache[ch_id] = webhook
            return webhook
    else:
        webhook = await channel.create_webhook(name="ASFeed")
        webhooks = await channel.webhooks()
        webhook_cache[ch_id] = webhook
        return webhook