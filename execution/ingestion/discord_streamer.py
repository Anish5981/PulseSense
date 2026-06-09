import os
import json
import asyncio
import discord
from dotenv import load_dotenv
from kafka_producer import PulseProducer

# 1. Load Configuration
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
KAFKA_TOPIC = "sentiment_stream"

class PulseDiscordClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.producer = PulseProducer()
        print("🚀 Discord Streamer Initialized...")

    async def on_ready(self):
        print(f"✅ Logged in as {self.user} (ID: {self.user.id})")
        print("📡 Listening for real-time messages...")

    async def on_message(self, message):
        # Ignore messages from the bot itself
        if message.author == self.user:
            return

        # Prepare message payload
        data = {
            "text": message.content,
            "source": f"discord/{message.guild.name if message.guild else 'DM'}",
            "author": str(message.author),
            "channel": str(message.channel)
        }

        # Send to Kafka
        print(f"📧 New Message from {data['author']}: {data['text'][:50]}...")
        self.producer.send_message(KAFKA_TOPIC, data)

if __name__ == "__main__":
    # Ensure Message Content Intent is enabled in Discord Portal!
    intents = discord.Intents.default()
    intents.message_content = True
    
    client = PulseDiscordClient(intents=intents)
    
    import time
    from backoff import exponential_backoff
    
    attempt = 0
    while True:
        try:
            client.run(TOKEN)
            break
        except Exception as e:
            print(f"❌ Discord Connection Error: {e}")
            delay = exponential_backoff(attempt)
            print(f"⏳ Retrying in {delay:.2f} seconds...")
            time.sleep(delay)
            attempt += 1
        finally:
            if attempt == 0:
                print("🛑 Streamer Shutting Down...")
