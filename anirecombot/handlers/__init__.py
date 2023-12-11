from aiogram import Router


def setup_routers() -> Router:
    from . import (
        start_handler,
        return_to_menu,
        rnd_content_api,
        ani_recomms,
        picrandom,
        same_response,
    )

    router = Router()
    router.include_routers(start_handler.router)
    router.include_routers(return_to_menu.router)
    router.include_routers(rnd_content_api.router)
    router.include_routers(ani_recomms.router)
    router.include_routers(picrandom.router)
    router.include_routers(same_response.router)

    return router
