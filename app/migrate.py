import os
import sys
import traceback
import asyncio

from alembic import command
from alembic.config import Config

from src.config import create_config
from src.logger import logger


BASE_DIR = os.path.dirname(__file__)


def prepare_alembic_ini() -> Config:
    db_conf = create_config().postgres
    path = os.path.join(BASE_DIR, "alembic.ini")
    alembic_cfg = Config(path)
    alembic_cfg.set_main_option("sqlalchemy.url", db_conf.build_dsn())
    return alembic_cfg


def migrate() -> None:
    alembic_cfg = prepare_alembic_ini()
    command.revision(alembic_cfg, message="Auto-generated migration", autogenerate=True)
    command.upgrade(alembic_cfg, "head")
    logger.info("Postgres migration have done.")


async def run_migrations():
    # Для Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    await asyncio.to_thread(migrate)


if __name__ == "__main__":
    try:
        asyncio.run(run_migrations())
        logger.info("All migrations done successfully!")
    except Exception as exc:
        logger.error(f"Migration error. {exc!s} - {traceback.format_exc()}")
