import logging

logger = logging.getLogger(__name__)

async def init_database(db):
    """
    Initialize MongoDB indexes for optimal query performance.
    """
    # Users collection
    await db.users.create_index("email", unique=True)
    await db.users.create_index("id")
    logger.info("Users indexes created")
    
    # Scripts collection
    await db.scripts.create_index([("user_id", 1), ("created_at", -1)])
    await db.scripts.create_index("id")
    logger.info("Scripts indexes created")
    
    # Hooks collection
    await db.hooks.create_index([("user_id", 1), ("created_at", -1)])
    await db.hooks.create_index("id")
    await db.hooks.create_index("hook_type")
    logger.info("Hooks indexes created")
    
    # Metrics collection
    await db.metrics.create_index([("user_id", 1), ("created_at", -1)])
    await db.metrics.create_index("script_id")
    logger.info("Metrics indexes created")
    
    # Videos collection
    await db.videos.create_index([("user_id", 1), ("created_at", -1)])
    await db.videos.create_index("script_id")
    logger.info("Videos indexes created")
    
    # Analytics Data collection (Notion CSV imports)
    await db.analytics_data.create_index([("user_id", 1), ("retention_percent", -1)])
    await db.analytics_data.create_index("id")
    await db.analytics_data.create_index("social_file")
    logger.info("Analytics Data indexes created")