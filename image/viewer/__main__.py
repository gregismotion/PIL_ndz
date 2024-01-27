from PIL import Image

from pygame import Surface
from pygame.image import frombytes as surface_from_bytes
from pygame.transform import smoothscale as smoothscale_surface

from pygame.math import Vector2

from typing import List, TypeVar, Tuple

from itertools import chain

import math

T = TypeVar("T")
Grid = List[List[T]]

ImageGrid = Grid[type(Image)]

class SurfaceGrid(Grid[Surface]):
	@property
	def surfaces(self) -> List[Surface]:
		return list(chain(*self))
	
	@property
	def size(self) -> Tuple[int, int]:
		return self.get_size()
	def get_size(self) -> Tuple[int, int]:
		width = 0
		count = 0
		for row in self:
			width = max(width, sum([(column.get_size()[0] if column else 0) for column in row]))
			count = max(count, len(row))
		height = 0
		for i in range(count):
			current = 0
			heights = []
			for row in self:
				heights.append((row[i].get_size()[1] if row[i] else 0) if len(row) >= count else 0)
			current = sum(heights)
			height = max(height, current) 
		return (width, height)

def _downscale_surface_to_max(surface: Surface, max_diagonal: "natural_number"):
	origin = Vector2()
	size = surface.get_size()
	length = origin.distance_to(size)
	if length > max_diagonal and max_diagonal:
		props = max_diagonal / length
		return smoothscale_surface(surface, origin.lerp(size, props))
	else:
		return surface

def _find_row_num(count: int) -> int:
	sqrt_count = math.sqrt(count)
	return math.ceil(count / sqrt_count)
def _get_grid(*images: type(Image)) -> ImageGrid:
	count = len(images)
	row_count = _find_row_num(count)
	column_count = math.ceil(count / row_count)

	grid = [[None] * column_count for _ in range(row_count)]

	image_index = 0
	for row in range(row_count):
		for col in range(column_count):
			if image_index < count:
				grid[row][col] = images[image_index]
				image_index += 1
			else:
				break
	return grid

def _surface_grid_into_surface(grid: SurfaceGrid) -> Surface:
	final = Surface(grid.size)
	y = 0
	print(grid)
	for row in grid:
		height = 0
		x = 0
		for image in row:
			if image:
				final.blit(image, (x, y))
				size = image.get_size()
				x += size[0]			
				height = max(height, size[1])
		y += height
	return final

def _image_grid_into_surface_grid(grid: ImageGrid) -> SurfaceGrid:
	return SurfaceGrid([[(surface_from_bytes(img.tobytes(), img.size, img.mode) if img else None) for img in row] for row in grid])

def _get_preview_surface(grid: ImageGrid, max_diagonal: "natural_number") -> Surface:
	grid = _image_grid_into_surface_grid(grid)
	surface = _surface_grid_into_surface(grid)
	return _downscale_surface_to_max(surface, max_diagonal)

def _get_full_surface(grid: ImageGrid) -> Surface:
	pass

def viewer(max_diagonal: "natural_number" = 512, *images: type(Image)) -> [
	{ "name": "full_surface", "type": Surface, "viz": "loop" },
	{ "name": "preview_surface", "type": Surface, "viz": "side" }
]:
	full_surface = None
	preview_surface = None
	
	count = len(images)
	if count == 1:
		image = images[0]

		full_surface = surface_from_bytes(image.tobytes(), image.size, image.mode)
		preview_surface = _downscale_surface_to_max(full_surface, max_diagonal)
	else:
		grid = _get_grid(*images)
		full_surface = _get_full_surface(grid)
		preview_surface = _get_preview_surface(grid, max_diagonal)

	return { "full_surface": full_surface, "preview_surface": preview_surface }

main_callable = viewer
