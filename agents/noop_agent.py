from library import IDABot


class NoOpAgent(IDABot):
    def __init__(self):
        IDABot.__init__(self)

    def on_game_start(self) -> None:
        IDABot.on_game_start(self)

    def on_step(self) -> None:
        IDABot.on_step(self)
