import os
import asyncio
import aio_pika

AMQP_URL = os.getenv("AMQP_URL", "amqp://guest:guest@localhost:5672/")
QUEUE_NAME = os.getenv("HELLO_QUEUE", "hello.queue")

async def main():
    connection = await aio_pika.connect_robust(AMQP_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)

    print(f"[*] Waiting for messages on {QUEUE_NAME} (Ctrl+C to stop)")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                print("[x] Received:", message.body.decode("utf-8"))

if __name__ == "__main__":
    asyncio.run(main())
