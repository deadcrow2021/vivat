import logging

from src.config import create_config


config = create_config()

logger = logging.getLogger('logger')
logger.handlers = []
logger.setLevel(config.app.log_level)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
