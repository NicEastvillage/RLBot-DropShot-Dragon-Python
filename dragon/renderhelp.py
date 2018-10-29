from RLUtilities.LinearAlgebra import vec3

import tiles


def highlight_tile(renderer, tile, color):
    vecs = [tile.location + vec3(tiles.TILE_WIDTH / 2, tiles.TILE_SIZE / 2, 0),
            tile.location + vec3(0, tiles.TILE_SIZE, 0),
            tile.location + vec3(-tiles.TILE_WIDTH / 2, tiles.TILE_SIZE / 2, 0),
            tile.location + vec3(-tiles.TILE_WIDTH / 2, -tiles.TILE_SIZE / 2, 0),
            tile.location + vec3(0, -tiles.TILE_SIZE, 0),
            tile.location + vec3(tiles.TILE_WIDTH / 2, -tiles.TILE_SIZE / 2, 0),
            tile.location + vec3(tiles.TILE_WIDTH / 2, tiles.TILE_SIZE / 2, 0)]
    renderer.draw_polyline_3d(vecs, color)


def highlight_tile_more(renderer, tile, color):
    vecs = [tile.location + vec3(tiles.TILE_WIDTH / 2, tiles.TILE_SIZE / 2, 0),
            tile.location + vec3(0, tiles.TILE_SIZE, 0),
            tile.location + vec3(-tiles.TILE_WIDTH / 2, tiles.TILE_SIZE / 2, 0),
            tile.location + vec3(-tiles.TILE_WIDTH / 2, -tiles.TILE_SIZE / 2, 0),
            tile.location + vec3(0, -tiles.TILE_SIZE, 0),
            tile.location + vec3(tiles.TILE_WIDTH / 2, -tiles.TILE_SIZE / 2, 0)]

    for i in range(6):
        for j in range(i + 1, 6):
            renderer.draw_line_3d(vecs[i], vecs[j], color)


def highlight_point_on_tile(renderer, info, point, color):
    flat = vec3(point[0], point[1], 0)
    tile = tiles.point_to_tile(info, point)
    renderer.draw_line_3d(point, flat, color)
    if tile != None:
        vecs = [tile.location + vec3(tiles.TILE_WIDTH / 2, tiles.TILE_SIZE / 2, 0),
                tile.location + vec3(0, tiles.TILE_SIZE, 0),
                tile.location + vec3(-tiles.TILE_WIDTH / 2, tiles.TILE_SIZE / 2, 0),
                tile.location + vec3(-tiles.TILE_WIDTH / 2, -tiles.TILE_SIZE / 2, 0),
                tile.location + vec3(0, -tiles.TILE_SIZE, 0),
                tile.location + vec3(tiles.TILE_WIDTH / 2, -tiles.TILE_SIZE / 2, 0),
                tile.location + vec3(tiles.TILE_WIDTH / 2, tiles.TILE_SIZE / 2, 0)]
        renderer.draw_polyline_3d(vecs, color)
        for i in range(6):
            renderer.draw_line_3d(flat, vecs[i], color)
