
from RLUtilities.GameInfo import *
from tile import ALL_TILES


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
