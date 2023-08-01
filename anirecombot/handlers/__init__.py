from aiogram import Router


def setup_routers() -> Router:
    from . import (
        same_response,
        rnd_content_api,
        ani_recomms,
        start_handler
    )

    router = Router()
    router.include_routers(start_handler.router)
    router.include_routers(ani_recomms.router)
    router.include_routers(rnd_content_api.router)
    router.include_routers(same_response.router)

    return router
