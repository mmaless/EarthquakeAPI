import logging
from datetime import datetime

from config import LOGGING_LEVEL

logging.basicConfig(filename='Logs/{:%Y-%m-%d}.log'.format(datetime.now()),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=LOGGING_LEVEL)

log = logging.getLogger(__name__)
