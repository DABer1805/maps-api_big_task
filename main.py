import pygame
import requests
from io import BytesIO

# Задаем координаты и масштаб карты
latitude = 55.75396
longitude = 37.620393
zoom = 10

# Формируем URL запрос к Maps API
url = f"https://static-maps.yandex.ru/1.x/?ll=" \
      f"{longitude},{latitude}&z={zoom}&l=map"

response = requests.get(url)
# Грузим нашу картинку
map_image = pygame.image.load(BytesIO(response.content))

# Создаем окно Pygame
pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Большая задача по Maps API. Часть №1")

# Отображаем карту в окне
screen.blit(map_image, (0, 0))
pygame.display.flip()

# Основной цикл приложения
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()