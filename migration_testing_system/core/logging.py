import logging

from .settings import settings

logger = logging.getLogger("migrations_testing_system")
logger.setLevel(settings.log_level)
