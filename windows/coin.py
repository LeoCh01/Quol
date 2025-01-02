from components.custom_window import CustomWindow


class Coin(CustomWindow):
    def __init__(self, geometry):
        super().__init__('Coin Flip', geometry)
