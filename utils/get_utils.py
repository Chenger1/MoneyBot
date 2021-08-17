from db.models import Utils


async def get_percentage() -> int:
    utils = await Utils.load()
    return utils.default_percent
