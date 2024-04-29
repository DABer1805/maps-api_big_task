import pygame
import requests
from io import BytesIO

# Теперь, если кликать по переключателю почтового индекса, то он будет
# автоматически добавляться / убираться, без необходимости заново
# производить поиск по кнопке

# ул. Петровка, 38, стр. 9, Москва - пример для теста почтового индекса

# Задаем координаты, масштаб и предельные значения карты
latitude = 55.75396
longitude = 37.620393
zoom = 10
MIN_ZOOM = 1
MAX_ZOOM = 19
LATITUDE_STEP = 0.005
LONGITUDE_STEP = 0.005
FPS = 60  # Частота кадров

WIDTH, HEIGHT = 600, 578

COLOR_ACTIVE = pygame.Color('#ffeba0')
COLOR_PASSIVE = pygame.Color('#e6e6e6')

POSTAL_COLOR_ACTIVE = pygame.Color('#c8ffa0')
POSTAL_COLOR_PASSIVE = pygame.Color('#ffa0a0')

FONT_COLOR = pygame.Color('#9b9a95')
POSTAL_CODE_FONT_COLOR = pygame.Color('white')

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
pygame.display.set_caption("Большая задача по Maps API. Часть №10")

base_font = pygame.font.Font(None, 32)
user_text = ''
address_text = ''
postal_code = ''

# Поле ввода
input_rect = pygame.Rect(0, 0, WIDTH, 32)
# Поле вывода для адреса найденного объекта
address_rect = pygame.Rect(0, 32, WIDTH, 32)
# Кнопка сброса
reset_button = pygame.Rect(0, 64, WIDTH, 32)
# Переключатель почтового индекса
postal_code_button = pygame.Rect(0, 96, WIDTH, 32)

postal_code_button_color = POSTAL_COLOR_PASSIVE

input_rect_color = COLOR_PASSIVE
reset_button_color = COLOR_PASSIVE

# Активно ли поле ввода
input_rect_active = False
# Активна ли кнопка сброса
reset_button_active = False
# Активно ли приписывание почтового индекса
postal_code_on = False

# Отображаем карту в окне
screen.blit(map_image, (0, 128))
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
    screen.blit(map_image, (0, 128))


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
    global point, address_text, postal_code
    # Формируем URL запрос для поиска объекта
    url = f"https://geocode-maps.yandex.ru/1.x/?apikey={API_KEY}" \
          f"&geocode={query}&format=json"
    response = requests.get(url).json()
    if response.get("response"):
        # Получаем координаты объекта
        object_data = response["response"]["GeoObjectCollection"][
            "featureMember"]
        if object_data:
            object_first = object_data[0]["GeoObject"]
            address = object_first["metaDataProperty"]["GeocoderMetaData"][
                "Address"]
            address_text = address["formatted"]
            postal_code = address.get('postal_code')
            coords = object_first["Point"]["pos"].split()
            longitude = float(coords[0])
            latitude = float(coords[1])
            point = f'{longitude},{latitude},comma'
            # Перемещаем карту на центральную точку объекта
            update_map(
                latitude, longitude, zoom, layer,
            )
        else:
            address_text = 'Не найдено :('
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
                user_text = ''
                address_text = ''
                postal_code = ''
                update_map(latitude, longitude, zoom, current_layer)
            else:
                reset_button_active = False
            if input_rect.collidepoint(event.pos):
                input_rect_active = True
            else:
                input_rect_active = False
            if postal_code_button.collidepoint(event.pos):
                postal_code_on = not postal_code_on
                splited_address = address_text.split(',')
                if len(splited_address) > 1 and \
                        splited_address[-1].isdigit():
                    address_text = ''
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
                    char = event.unicode
                    if char.isalnum() or char in (' ', ',', '.'):
                        user_text += event.unicode

        if input_rect_active:
            input_rect_color = COLOR_ACTIVE
        else:
            input_rect_color = COLOR_PASSIVE

        if reset_button_active:
            reset_button_color = COLOR_ACTIVE
        else:
            reset_button_color = COLOR_PASSIVE

        if postal_code_on:
            postal_code_button_color = POSTAL_COLOR_ACTIVE
        else:
            postal_code_button_color = POSTAL_COLOR_PASSIVE

        # Рисуем поле ввода
        pygame.draw.rect(screen, input_rect_color, input_rect)
        # Рисуем поле вывода адреса найденного объекта
        pygame.draw.rect(screen, COLOR_PASSIVE, address_rect)
        # Рисуем кнопку сброса
        pygame.draw.rect(screen, reset_button_color, reset_button)
        # Рисуем кнопку переключателя почтового индекса
        pygame.draw.rect(screen, postal_code_button_color,
                         postal_code_button)

        # Текст поля ввода
        text_surface = base_font.render(
            user_text, True, FONT_COLOR
        )

        full_adrress = address_text
        if postal_code_on and postal_code:
            full_adrress += f', {postal_code}'

        # Текст полного адреса найденного объекта
        address_text_surface = base_font.render(
            full_adrress, True, FONT_COLOR
        )
        # Текст кнопки сброса
        reset_button_text_surface = base_font.render(
            'Сбросить результаты поиска', True, FONT_COLOR
        )
        # Текст кнопки переключателя почтового индекса
        postal_code_text_surface = base_font.render(
            'Почтовый индекс', True, POSTAL_CODE_FONT_COLOR
        )

        # Отображаем текст нашего поля ввода
        screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
        # Отображаем текст адреса
        screen.blit(address_text_surface, (address_rect.x + 5, 37))
        # Отображаем текст кнопки
        screen.blit(reset_button_text_surface, (136, 69))
        # Отображаем текст кнопки переключателя почтового индекса
        screen.blit(postal_code_text_surface, (189, 101))

        # Ограничение частоты кадров
        pygame.display.flip()
        clock.tick(FPS)

pygame.quit()
