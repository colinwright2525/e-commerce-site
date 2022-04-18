
class Boardgame:
    def __init__(self, id, name, description, price, image):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.image = image

descriptions = {
    'Monopoly': 'Monopoly is a real-estate board game for two to eight players. The player\'s goal is to remain financially solvent while forcing opponents into bankruptcy by buying and developing pieces of property. Bankruptcy results in elimination from the game. The last player remaining on the board is the winner.',
    'Scrabble': 'Scrabble, board-and-tile game in which two to four players compete in forming words with lettered tiles on a 225-square board; words spelled out by letters on the tiles interlock like words in a crossword puzzle. Players draw seven tiles from a pool at the start and replenish their supply after each turn.',
    'Clue': 'Cluedo — known as Clue in North America — is a murder mystery game for three to six players, devised by Anthony E. Pratt fromBirmingham, England, and currently published by the American game and toy company Hasbro. The object of the game is to determine who murdered the game\'s victim, where the crime took place, and which weapon was used.',
    'Risk': 'In the Risk game, the goal is simple: players aim to conquer their enemies\' territories by building an army, moving their troops in, and engaging in battle. Depending on the roll of the dice, a player will either defeat the enemy or be defeated.',
}