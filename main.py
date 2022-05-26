import os
import sys

os.chdir(sys.path[0])
sys.path.insert(1, "P://Python Projects/assets/")

from GameObjects import *
from colors import Color



class IsoGrid:
	transparent_img = pg.image.load("transparent.png")
	select_img = pg.image.load("select.png")

	class Tile:
		def __init__(self, x, y, img, i, j):
			self.screen_pos = i, j
			self.pos = (x, y)
			self.img = img

		def Draw(self, edit_mode):
			mouse_x, mouse_y = pg.mouse.get_pos()
			w, h = self.img.get_width(), self.img.get_height()
			if edit_mode:
				if pg.Rect(self.pos[0], self.pos[1], w, h).collidepoint((mouse_x, mouse_y)):
					if Vec2(mouse_x, mouse_y).GetEDistance((self.pos[0] + w // 2, self.pos[1] + h // 4)) <= w / 5:
						img = self.img.copy()
						img.blit(pg.transform.scale(IsoGrid.transparent_img, (w, h)), (0, 0))
						screen.blit(img, self.pos)

						return

			screen.blit(self.img, self.pos)

	def __init__(self, rect=(200, 200, width-200, height-200), gridSize=(10, 10, 1), tileFolder="tiles/", imageScale=(100, 100)):
		self.rect = pg.Rect(rect)
		self.tileFolder = tileFolder
		
		self.w, self.h = imageScale
		self.offset_x = Vec2(0.5 * self.w, -0.5 * self.w)
		self.offset_y = Vec2(0.25 * self.h, 0.25 * self.h)

		self.gridSize = gridSize

		self.edit_mode = True

		self.x, self.y, self.z = 0, 0, 0

		self.tiles = {}
		for i, file in enumerate(GetAllFilesInFolder(self.tileFolder)):
			name = file.split("_")[1].split(".")[0]
			self.tiles[name] = pg.transform.scale(pg.image.load(self.tileFolder + file), imageScale)
			
			Button((0, int(file.split("_")[0]) * 60, 200, 60), (lightBlack, darkWhite, lightBlue), text=name, onClick=self.ChangePaintTile, onClickArgs=[name], textData={"alignText": "left"})
			Image((200 - 55, int(file.split("_")[0]) * 60 + 5, 50, 50), self.tileFolder + file)

		self.gridTiles = [[[None for i in range(self.gridSize[0])] for j in range(self.gridSize[1])] for k in range(self.gridSize[2])]
		self.selected_paint_tile = self.tiles["water"]
		self.x_scroll = 0
		self.y_scoll = 0
		self.UpdateGrid()

		self.seed_input = TextInputBox((210, 0, 300, 40), (lightBlack, darkWhite, lightBlue), "Seed: ", drawData={"replaceSplashText": False}, textData={"alignText": "left"}, inputData={"nonAllowedKeysFilePath": "P:\\Python Projects\\assets\\input keys\\special.txt", "closeOnMissInput": False})
		Button((510, 0, 200, 40), (lightBlack, darkWhite, lightBlue), text="Generate", onClick=self.Generate)
		self.Generate()

	def Generate(self):
		seed = self.seed_input.input
		if len(seed.strip(" ")) == 0:
			seed = randint(0, 10000000000)
			self.seed_input.UpdateText(f"Seed: {seed}")

		Noise.SetSeed(seed)

		for i in range(self.gridSize[0]):
			for j in range(self.gridSize[1]):
				for k in range(self.gridSize[2]):
					x, y = self.TransposeWorldToScreenSpace(i, j, k)
					self.gridTiles[k][j][i] = self.Noise(x, y, k, i, j)		

	def TransposeWorldToScreenSpace(self, x, y, k):
		return ((x * self.offset_x.x + y * self.offset_x.y) + (self.rect.x + self.rect.w // 2) - self.w // 2), ((x * self.offset_y.x + y * self.offset_y.y) + (self.rect.y + self.rect.h // 2) - self.gridSize[1] * 0.3 * self.h) - (k * self.h / 1.87)

	def Noise(self, x, y, z, i, j):
		noise = Noise.PerlinNoise(x / 10, y / 10, z / 10)
		features = Noise.PerlinNoise(x / 100, y / 100, z / 100)
		feature_variation = Noise.PerlinNoise(x, y, z)
		x -= self.x_scroll
		y -= self.y_scoll
		if self.gridSize[2] > 1:
			if z == 0:
				if feature_variation > 0.5:
					tile = self.tiles["cobblestone"]
				else:
					tile = self.tiles["stone"]
			elif z == 2:
				if noise <= 0.4:
					tile = self.tiles["water"]
				else:
					if 0 <= features < 0.4:
						tile = self.tiles["grass"]
					elif 0.4 <= features < 0.6:
						tile = self.tiles["overgrown grass"]
					elif 0.6 <= features <= 1:
						tile = self.tiles["flowery grass"]
			else:
				if features <= 0.05:
					if feature_variation > 0.5:
						tile = self.tiles["cobblestone"]
					else:
						tile = self.tiles["stone"]
				elif features >= 0.3:
					tile = self.tiles["dirt"]
				else:
					tile = self.tiles["grass"]
		else:
			if 0 <= noise < 0.3:
				tile = self.tiles["water"]
			elif 0.3 <= noise < 0.35:
				tile = self.tiles["dirt"]
			elif 0.35 <= noise < 0.8:
				if 0 <= feature_variation < 0.5:
					tile = self.tiles["grass"]
				elif 0.5 <= feature_variation < 0.8:
					tile = self.tiles["overgrown grass"]
				elif 0.8 <= feature_variation:
					tile = self.tiles["flowery grass"]
			elif 0.8 <= noise:
				if feature_variation > 0.5:
					tile = self.tiles["cobblestone"]
				else:
					tile = self.tiles["stone"]

		return IsoGrid.Tile(x, y, tile, i, j)

	def UpdateGrid(self):
		for i in range(self.gridSize[0]):
			for j in range(self.gridSize[1]):
				for k in range(self.gridSize[2]):
					x, y = self.TransposeWorldToScreenSpace(i, j, k)
					if self.gridTiles[k][j][i] == None:
						self.gridTiles[k][j][i] = self.Noise(x, y, k, i, j)
					else:
						self.gridTiles[k][j][i].pos = (x, y)

	def Draw(self):
		for row in self.gridTiles:
			for col in row:
				for tile in col:
					tile.Draw(self.edit_mode)

		if not self.edit_mode:
			mouse_x, mouse_y = pg.mouse.get_pos()
			tile = self.GetTile(mouse_x, mouse_y)
			if tile != None:
				screen.blit(pg.transform.scale(IsoGrid.select_img, (self.w, self.h)), tile.pos)

	def HandleEvent(self, event):
		mouse_x, mouse_y = pg.mouse.get_pos()

		if event.type == pg.KEYDOWN:
			if event.key == pg.K_F1:
				self.edit_mode = not self.edit_mode

		if pg.mouse.get_pressed()[0]:

			for i in range(self.gridSize[0]):
				for j in range(self.gridSize[1]):
					for k in range(self.gridSize[2]):	
						tile = self.gridTiles[k][j][i]

						x, y = tile.pos[0], tile.pos[1]
						if pg.Rect(x, y, self.w, self.h).collidepoint((mouse_x, mouse_y)):
							if Vec2(mouse_x, mouse_y).GetEDistance((x + self.w // 2, y + self.h // 4)) <= self.w / 5:
								if self.edit_mode:
									self.PlaceTile(i, j, k, self.selected_paint_tile)

	def PlaceTile(self, i, j, k, tile):
		self.gridTiles[k][j][i].pos = (self.TransposeWorldToScreenSpace(i, j, k))
		self.gridTiles[k][j][i].img = tile

	def GetTile(self, x, y):
		for i in range(self.gridSize[0]):
			for j in range(self.gridSize[1]):
				for k in range(self.gridSize[2]):
					tile = self.gridTiles[k][j][i]
					if pg.Rect(tile.pos[0], tile.pos[1], self.w, self.h).collidepoint((x, y)):
						if Vec2(x, y).GetEDistance((tile.pos[0] + self.w // 2, tile.pos[1] + self.h // 4)) <= self.w / 5:
							return tile

	def ChangePaintTile(self, tile_index):
		self.selected_paint_tile = self.tiles[tile_index]


class Player:
	def __init__(self, pos, img_prefix, floor, folder="player/"):
		self.pos = Vec2(pos[0], pos[1])
		self.imgs = {}
		self.floor = floor
		for file in GetAllFilesInFolder(folder):
			if img_prefix in file:
				self.imgs[file.split("_")[1].split(".")[0]] = pg.transform.scale(pg.image.load(folder + file), (self.floor.w, self.floor.h))
		self.speed = 0.05
		self.img = self.imgs["idle"]
		self.selected_tile = None

	def Draw(self):
		screen.blit(self.img, self.floor.TransposeWorldToScreenSpace(self.pos[0], self.pos[1], 1))
		self.Move()
		if self.selected_tile == None:
			self.img = self.imgs["idle"]

	def HandleEvent(self, event):
		if not self.floor.edit_mode:
			if event.type == pg.MOUSEBUTTONDOWN:
				mouse_x, mouse_y = pg.mouse.get_pos()
				self.selected_tile = self.floor.GetTile(mouse_x, mouse_y)

	def Move(self):
		if self.selected_tile != None:
			pos = (round(self.pos[0]), round(self.pos[1]))
			tile_pos = (self.selected_tile.screen_pos[0], self.selected_tile.screen_pos[1])
			diff = (round(tile_pos[0] - pos[0], 1), round(tile_pos[1] - pos[1], 1))
			if diff[0] < 1 and diff[1] < 1:
				pos = self.pos
				diff = (round(tile_pos[0] - pos[0], 1), round(tile_pos[1] - pos[1], 1))
			if diff[0] == 0 and diff[1] == 0:
				self.selected_tile = None
			else:
				x_sign, y_sign = copysign(1, diff[0]), copysign(1, diff[1])
				if round(diff[0] - int(diff[0]), 3) != 0:
					self.pos.x += x_sign * self.speed
					if x_sign == -1:
						self.img = self.imgs["left"]
					else:
						self.img = self.imgs["right"]
				elif round(diff[1] - int(diff[1]), 3) != 0:
					self.pos.y += y_sign * self.speed
					if y_sign == -1:
						self.img = self.imgs["up"]
					else:
						self.img = self.imgs["down"]
				else:
					if abs(diff[0]) >= abs(diff[1]):
						self.pos.x += x_sign * self.speed
						if x_sign == -1:
							self.img = self.imgs["left"]
						else:
							self.img = self.imgs["right"]
					else:
						self.pos.y += y_sign * self.speed
						if y_sign == -1:
							self.img = self.imgs["up"]
						else:
							self.img = self.imgs["down"]


IGrid = IsoGrid(gridSize=(10, 10, 1))
p = Player((0, 0), "player", IGrid)


def DrawLoop():
	screen.fill(darkGray)


	DrawAllGUIObjects()
	
	for img in allImages:
		img.Draw()

	IGrid.Draw()
	p.Draw()

	pg.display.update()


def HandleEvents(event):
	HandleGui(event)

	if event.type == pg.KEYDOWN:
		if event.key == pg.K_SPACE:
			print(clock.get_fps())

	IGrid.HandleEvent(event)

	p.HandleEvent(event)


while RUNNING:
	clock.tick_busy_loop(FPS)
	deltaTime = clock.get_time()
	for event in pg.event.get():
		if event.type == pg.QUIT:
			RUNNING = False
		if event.type == pg.KEYDOWN:
			if event.key == pg.K_ESCAPE:
				RUNNING = False

		HandleEvents(event)

	DrawLoop()

