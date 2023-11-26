import asyncio
import json

import httpx


async def main() -> None:
    host = "http://127.0.0.1:8000"

    with open("./example/consumers.json") as consumers_file:
        consumers_data = json.load(consumers_file)

        for consumer in consumers_data:
            payload = {"name": consumer["name"], "priority": consumer["priority"]}
            url = f"{host}/api/consumer/"

            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()

                consumer_id = response.json()["id"]

            for component in consumer["components"]:
                payload = {
                    "name": component["name"],
                    "consumption": component["consumption"],
                    "running": False,
                    "ip": component["ip"],
                    "relais": component["relais"],
                }
                url = f"{host}/api/consumer/{consumer_id}/component/"

                async with httpx.AsyncClient() as client:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()


if __name__ == "__main__":
    asyncio.run(main())
