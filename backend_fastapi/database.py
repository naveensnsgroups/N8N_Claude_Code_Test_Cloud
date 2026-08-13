"""
MongoDB connection and database initialization using Motor (async MongoDB driver).
"""
from motor.motor_asyncio import AsyncClient, AsyncDatabase
from config import get_settings
import logging

logger = logging.getLogger(__name__)

# Global database instance
db: AsyncDatabase = None


async def connect_to_mongo() -> AsyncDatabase:
    """
    Establish connection to MongoDB Atlas.
    Returns the database instance.
    """
    global db
    settings = get_settings()

    if not settings.mongo_uri:
        logger.error('MONGO_URI is not defined in environment variables.')
        raise ValueError('MONGO_URI is not defined in environment variables.')

    try:
        client = AsyncClient(settings.mongo_uri)
        # Verify connection
        await client.admin.command('ping')

        db = client.get_database()
        logger.info(f'MongoDB Atlas Connected successfully')
        return db
    except Exception as error:
        logger.error(f'MongoDB Connection Error: {str(error)}')
        raise


async def close_mongo_connection() -> None:
    """Close the MongoDB connection."""
    global db
    if db is not None:
        db.client.close()
        logger.info('MongoDB connection closed')


def get_database() -> AsyncDatabase:
    """Get the current database instance."""
    if db is None:
        raise RuntimeError('Database not connected. Call connect_to_mongo() first.')
    return db
