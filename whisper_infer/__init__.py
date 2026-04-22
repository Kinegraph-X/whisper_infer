import logging
from whisper_infer.context import config

logging.basicConfig(
    level=config.log_level,
    format="%(asctime)s [%(name)s] %(levelname)s — %(message)s"
)