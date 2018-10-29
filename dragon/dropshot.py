import math

from RLUtilities.GameInfo import *
from tiles import ALL_TILES


TO_WALL = 4555
TO_CORNER = 2 * TO_WALL / math.sqrt(3)
TO_CORNER_ROUNDED = 5026
HEIGHT = 2018


class DropshotInfo(GameInfo):
    def __init__(self, index, team):
        super().__init__(index, team)

        self.tile_dict = {}
        self.tile_list = ALL_TILES
        for tile in self.tile_list:
            self.tile_dict[tile.hex] = tile

    def read_packet(self, packet):
        super().read_packet(packet)

        for i in range(packet.num_tiles):
            self.tile_list[i].state = packet.dropshot_tiles[i].tile_state
