
from . import client, admin, basic


def setup(dp, bot):
    client.setup(dp, bot)
    admin.setup(dp, bot)
    basic.setup(dp, bot)
