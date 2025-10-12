
parking_difficulty_levels = {
    1: "Fácil",
    2: "Difícil",
    3: "Desconocida"
}
class Location:
    def __init__(self, name, map_link=None, parking_difficulty=None):
        self.name = name
        self.map_link = map_link
        self.parking_difficulty = parking_difficulty if parking_difficulty in parking_difficulty_levels else parking_difficulty_levels[3]

    def __str__(self):
        s = f"🏟 <a href='{self.map_link}'>{self.name}</a>\n"
        s += f"🚗 Dificultad de aparcamiento: {self.parking_difficulty}\n"
        return s
