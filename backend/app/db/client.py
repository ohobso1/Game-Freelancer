from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings


client: AsyncIOMotorClient | None = None
database: AsyncIOMotorDatabase | None = None


def connect_to_mongo() -> None:
    global client, database

    if not settings.mongodb_uri:
        raise RuntimeError("MONGODB_URI is not configured.")

    client = AsyncIOMotorClient(settings.mongodb_uri)
    database = client[settings.mongodb_database]


def disconnect_mongo() -> None:
    global client, database

    if client is not None:
        client.close()

    client = None
    database = None


def get_database() -> AsyncIOMotorDatabase:
    if database is None:
        raise RuntimeError("MongoDB is not connected. Call connect_to_mongo() first.")

    return database
