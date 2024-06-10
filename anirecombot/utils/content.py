import pathlib
from logging import getLogger

logger = getLogger(__name__)


async def get_image_extension(url: str) -> str:
    path = pathlib.Path(url)
    image_extension = path.suffix[1:]
    logger.debug('Image extension: %s', image_extension)

    return image_extension
