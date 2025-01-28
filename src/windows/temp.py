from src.components.custom_window import CustomWindow


class Temp(CustomWindow):
    def __init__(self, wid, geometry=(0, 0, 0, 0)):
        super().__init__('Temp', wid, geometry)
