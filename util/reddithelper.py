import asyncpraw
import os

reddit = asyncpraw.Reddit(
    client_id=os.getenv("RDTCLID"),
    client_secret=os.getenv("RDTCLSECRET"),
    user_agent="anthroswim",
    username="as-bot",
    password=os.getenv("RDTPASSWORD"),
)



