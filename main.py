import pygame
import requests
from io import BytesIO

# Задаем координаты, масштаб и предельные значения карты
latitude = 55.75396
longitude = 37.620393
zoom = 10
MIN_ZOOM = 1
MAX_ZOOM = 19
LATITUDE_STEP = 0.005
LONGITUDE_STEP = 0.005
FPS = 60  # Частота кадров

WIDTH, HEIGHT = 600, 514

COLOR_ACTIVE = pygame.Color('#ffeba0')
COLOR_PASSIVE = pygame.Color('#e6e6e6')

FONT_COLOR = pygame.Color('#9b9a95')

UP = 0
DOWN = 1
RIGHT = 2
LEFT = 3

API_KEY = "40d1649f-0493-4b70-98ba-98533de7710b"

# Слои карты
LAYERS = ["map", "sat", "sat,skl"]
current_layer = 0

# Формируем URL запрос к MapsAPI
url = f"https://static-maps.yandex.ru/1.x/?ll={longitude},{latitude}" \
      f"&z={zoom}&l={LAYERS[current_layer]}"

response = requests.get(url)
# Грузим нашу картинку
map_image = pygame.image.load(BytesIO(response.content))

# Создаем окно Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Большая задача по Maps API. Часть №7")

base_font = pygame.font.Font(None, 32)
user_text = ''

# Поле ввода
input_rect = pygame.Rect(0, 0, WIDTH, 32)
# Кнопка сброса
reset_button = pygame.Rect(0, 32, WIDTH, 32)

input_rect_color = COLOR_PASSIVE
reset_button_color = COLOR_PASSIVE

# Активно ли поле ввода
input_rect_active = False
# Активна ли кнопка сброса
reset_button_active = False

# Отображаем карту в окне
screen.blit(map_image, (0, 64))
pygame.display.flip()

clock = pygame.time.Clock()

point = None


def update_map(latitude, longitude, zoom, layer):
    # Формируем новый URL запрос
    url = f"https://static-maps.yandex.ru/1.x/" \
          f"?ll={longitude},{latitude}&z={zoom}&l=" \
          f"{LAYERS[layer]}"
    if point:
        url += f"&pt={point}"
    response = requests.get(url)
    # Грузим обновленную картинку
    map_image = pygame.image.load(BytesIO(response.content))
    # Отображаем обновленную карту в окне
    screen.blit(map_image, (0, 64))


def move_map(latitude, longitude, zoom, layer, direction=None):
    """ Перемещаем карту """
    if direction == UP:
        if not (latitude < 90 - LATITUDE_STEP):
            return latitude, longitude
        latitude += LATITUDE_STEP
    elif direction == DOWN:
        if not (latitude > -90 + LATITUDE_STEP):
            return latitude, longitude
        latitude -= LATITUDE_STEP
    elif direction == RIGHT:
        if not (longitude < 180 - LONGITUDE_STEP):
            return latitude, longitude
        longitude += LONGITUDE_STEP
    elif direction == LEFT:
        if not (longitude > -180 + LONGITUDE_STEP):
            return latitude, longitude
        longitude -= LONGITUDE_STEP
    update_map(latitude, longitude, zoom, layer)
    return latitude, longitude


def change_layer(latitude, longitude, zoom, layer):
    # Переключаем слой карты
    layer = (layer + 1) % len(LAYERS)
    # Формируем новый URL запрос
    update_map(latitude, longitude, zoom, layer)
    return layer


def find_object(latitude, longitude, zoom, layer, query):
    global point
    # Формируем URL запрос для поиска объекта
    url = f"https://geocode-maps.yandex.ru/1.x/?apikey={API_KEY}" \
          f"&geocode={query}&format=json"
    response = requests.get(url).json()
    if response.get("response"):
        # Получаем координаты объекта
        object_data = response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]["Point"]["pos"].split()
        longitude = float(object_data[0])
        latitude = float(object_data[1])
        point = f'{longitude},{latitude},comma'
        # Перемещаем карту на центральную точку объекта
        update_map(
            latitude, longitude, zoom, layer,
        )
    return latitude, longitude


# Основной цикл приложения
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if reset_button.collidepoint(event.pos):
                reset_button_active = True
                point = None
                update_map(latitude, longitude, zoom, current_layer)
            else:
                reset_button_active = False
            if input_rect.collidepoint(event.pos):
                input_rect_active = True
            else:
                input_rect_active = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEUP:
                # Увеличиваем масштаб
                if zoom < MAX_ZOOM:
                    zoom += 1
                    update_map(latitude, longitude, zoom, current_layer)
            elif event.key == pygame.K_PAGEDOWN:
                # Уменьшаем масштаб
                if zoom > MIN_ZOOM:
                    zoom -= 1
                    update_map(latitude, longitude, zoom, current_layer)
            elif event.key == pygame.K_UP:
                # Перемещаем центр карты вверх
                latitude, longitude = move_map(latitude, longitude,
                                               zoom, current_layer, UP)
            elif event.key == pygame.K_DOWN:
                # Перемещаем центр карты вниз
                latitude, longitude = move_map(latitude, longitude,
                                               zoom, current_layer, DOWN)
            elif event.key == pygame.K_LEFT:
                # Перемещаем карту влево
                latitude, longitude = move_map(latitude, longitude,
                                               zoom, current_layer, LEFT)
            elif event.key == pygame.K_RIGHT:
                # Перемещаем карту вправо
                latitude, longitude = move_map(latitude, longitude,
                                               zoom, current_layer, RIGHT)
            elif event.key == pygame.K_TAB:
                current_layer = change_layer(latitude, longitude, zoom,
                                             current_layer)
            elif event.key == pygame.K_RSHIFT:
                # Поиск объекта
                latitude, longitude = find_object(
                    latitude, longitude, zoom, current_layer, user_text
                )
            elif event.key == pygame.K_BACKSPACE:
                user_text = user_text[:-1]
            else:
                if len(user_text) < 47:
                    user_text += event.unicode

        if input_rect_active:
            input_rect_color = COLOR_ACTIVE
        else:
            input_rect_color = COLOR_PASSIVE

        if reset_button_active:
            reset_button_color = COLOR_ACTIVE
        else:
            reset_button_color = COLOR_PASSIVE

        # Рисуем поле ввода
        pygame.draw.rect(screen, input_rect_color, input_rect)
        # Рисуем кнопку сброса
        pygame.draw.rect(screen, reset_button_color, reset_button)

        # Текст
        text_surface = base_font.render(
            user_text, True, FONT_COLOR
        )
        # Текст кнопки сброса
        reset_button_text_surface = base_font.render(
            'Сбросить результаты поиска', True, FONT_COLOR
        )

        # Отображаем текст нашего поля ввода
        screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
        # Отображаем текст кнопки
        screen.blit(reset_button_text_surface, (136, 37))

        # Ограничение частоты кадров
        pygame.display.flip()
        clock.tick(FPS)

pygame.quit()
