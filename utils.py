# =============================================================================
# КАСТОМНЫЙ TQDM (Формальность)
# =============================================================================

from tqdm.auto import tqdm
from typing import Any, Optional, Union 

class ParserTqdm(tqdm):
    """
    Кастомный прогресс-бар на базе ``tqdm.notebook``.

    Наследует весь API tqdm и добавляет:

    * Разумные дефолты для парсинга (цвет, единицы, сглаживание).
    * Метод :meth:`set_status` — удобное обновление postfix одним вызовом.

    Parameters
    ----------
    iterable : любой итерируемый объект, optional
        Коллекция для перебора. Если не передан — бар создаётся вручную
        и обновляется через ``bar.update(n)``.
    total : int, optional
        Общее количество шагов. Определяется автоматически из ``len(iterable)``,
        если не задан явно.
    desc : str
        Подпись слева от бара.
    unit : str
        Единица измерения шага (отображается в скорости, например «4.9 стр/s»).
    colour : str
        Цвет заполненной части бара. Любое CSS-имя или HEX («cyan», «#00ff00»).
    leave : bool
        ``True``  — бар остаётся после завершения.
        ``False`` — исчезает (используется для вложенных баров).
    position : int
        Строка отображения. 0 — верхний бар, 1 — под ним, и т.д.
        Нужно задавать явно при вложенных барах, чтобы они не перекрывались.
    **kwargs
        Любые параметры tqdm — передаются напрямую и переопределяют дефолты.

    Examples
    --------
    Ручное управление (без итерируемого):

        bar = ParserTqdm(total=100, desc="⬇️ Загрузка")
        for chunk in download():
            bar.update(len(chunk))
        bar.close()

    С обновлением статуса:

        for page in ParserTqdm(range(1, 51), desc="🌐 Каталог", unit="стр"):
            result = fetch(page)
            bar.set_status(url=result.url, код=result.status)
    """

    def __init__(
        self,
        iterable: Any = None,
        total: Optional[int] = None,
        desc: str = "📍 Парсинг",
        unit: str = "об",
        colour: str = "cyan",
        leave: bool = True,
        position: int = 0,
        **kwargs,
    ):
        defaults = dict(
            desc=desc,
            unit=unit,
            colour=colour,
            leave=leave,
            position=position,
            smoothing=0.15,   # сглаживание скорости: 0 = среднее за всё время, 1 = только последний шаг
            miniters=1,       # минимум шагов между перерисовками
            mininterval=0.05, # минимум секунд между перерисовками — плавность без нагрузки на CPU
        )
        defaults.update(kwargs)  # kwargs имеют приоритет — можно переопределить любой дефолт
        super().__init__(iterable=iterable, total=total, **defaults)

    def set_status(self, **fields: Any) -> None:
        """
        Обновить postfix-поля (правая часть бара) одним вызовом.

        Удобнее стандартного ``set_postfix`` — не нужно передавать словарь.

        Parameters
        ----------
        **fields
            Произвольные ключ=значение, отображаются справа от прогресса.

        Example
        -------
            for page in pages_tqdm(50):
                r = fetch(page)
                bar.set_status(статус=r.status_code, записей=len(r.data))
            # → 📄 Страницы:  42%|██████▌    | 21/50 [00:10<00:14, статус=200, записей=134]
        """
        self.set_postfix(**fields, refresh=True)

def _to_iterable(x: Union[int, Any]) -> Any:
    """
    Конвертирует int в ``range(x)``, остальное возвращает как есть.

    Позволяет передавать число напрямую в фабричные функции:
    ``nested_tqdm(50)`` вместо ``nested_tqdm(range(50))``.
    """
    return range(x) if isinstance(x, int) else x

def pages_tqdm(
    total_pages: int,
    desc: str = "📄 Страницы",
    start: int = 1,
) -> ParserTqdm:
    """
    Прогресс-бар для перебора страниц пагинации (1-based по умолчанию).

    Parameters
    ----------
    total_pages : int
        Общее количество страниц.
    desc : str
        Подпись бара.
    start : int
        Номер первой страницы (обычно 1, иногда 0).

    Example
    -------
        for page in pages_tqdm(100):
            data = api.get_page(page)   # page = 1, 2, 3, ..., 100
    """
    return ParserTqdm(
        range(start, total_pages + 1),
        total=total_pages,
        desc=desc,
        unit="стр",
    )


def items_tqdm(
    iterable: Union[int, Any],
    total: Optional[int] = None,
    desc: str = "🔍 Обработка",
) -> ParserTqdm:
    """
    Прогресс-бар для произвольного итерируемого объекта.

    Parameters
    ----------
    iterable : int или iterable
        Коллекция для перебора или число (будет преобразовано в ``range``).
    total : int, optional
        Длина итератора, если её нельзя определить автоматически
        (например, для генераторов).
    desc : str
        Подпись бара.

    Examples
    --------
        # Список компаний
        for c in items_tqdm(companies, desc="🏢 Компании"):
            parse(c)

        # Генератор (total обязателен)
        for row in items_tqdm(df.itertuples(), total=len(df), desc="📊 Строки"):
            process(row)
    """
    it = _to_iterable(iterable)
    inferred_total = total or (iterable if isinstance(iterable, int) else None)
    return ParserTqdm(it, total=inferred_total, desc=desc, unit="эл")


def nested_tqdm(
    iterable: Union[int, Any],
    total: Optional[int] = None,
    desc: str = "↳ Вложенный",
    parent_position: int = 0,
) -> ParserTqdm:
    """
    Вложенный прогресс-бар, отображающийся под родительским.

    Автоматически исчезает после завершения (``leave=False``),
    чтобы не засорять вывод.

    Parameters
    ----------
    iterable : int или iterable
        Коллекция или число.
    total : int, optional
        Длина, если не определяется автоматически.
    desc : str
        Подпись бара.
    parent_position : int
        Позиция родительского бара (обычно 0).
        Вложенный встанет на ``parent_position + 1``.

    Example
    -------
        for page in pages_tqdm(10):                          # position=0
            for item in nested_tqdm(50, desc="↳ Товары"):   # position=1
                process(item)
        # Два бара обновляются на месте, не множась в строках.
    """
    it = _to_iterable(iterable)
    inferred_total = total or (iterable if isinstance(iterable, int) else None)
    return ParserTqdm(
        it,
        total=inferred_total,
        desc=desc,
        unit="эл",
        leave=False,                     # исчезает после завершения итерации
        position=parent_position + 1,    # строго под родителем
        colour="green",                  # визуально отличается от родительского
    )

# =============================================================================
# Инициализация драйвера (Настройки)
# =============================================================================

from seleniumbase import Driver

def init_driver(
    stealth_mode=True, 
    headless_mode=False, 
    proxy_str=None, 
    user_agent=None
):
    """
    Инициализирует и возвращает драйвер SeleniumBase с оптимальными настройками.
    Есть более умный подход с импортом SB - он тут не работает!
    """
    
    driver = Driver(
        # --- БАЗОВЫЕ НАСТРОЙКИ ---
        
        # Какой браузер использовать. 
        # Варианты: "chrome", "edge", "firefox", "safari".
        # Для обхода защит (UC Mode) Chrome поддерживается лучше всего.
        browser="chrome",
        
        # Режим "невидимки" (отсутствие графического интерфейса).
        # Варианты: 
        #   False  - браузер виден (максимальный траст от антифрод-систем, лучше всего для UC).
        #   True   - классический headless (легко палится защитами).
        #   "new"  - новый headless режим Chrome (компромисс: работает быстрее, палится реже, чем обычный True).
        headless=headless_mode,
        
        # --- НАСТРОЙКИ СКРЫТНОСТИ (STEALTH / UNDETECTED) ---
        
        # Включение Undetected-Chromedriver (UC Mode) от SeleniumBase.
        # Варианты: 
        #   True  - включает патчи драйвера для обхода Cloudflare/DataDome.
        #   False - обычный Selenium (если сайт без защит, работает быстрее и стабильнее).
        uc=stealth_mode,
        
        # Режим инкогнито.
        # Варианты: True / False.
        # True дает чистую сессию без старых кук и кэша, что часто помогает избежать 
        # теневых банов (shadowbans) при частых перезапусках скрипта.
        incognito=True,
        
        # Подмена User-Agent.
        # Варианты: строка (например, "Mozilla/5.0..."), либо None (оставить браузерный по умолчанию).
        # Внимание: в UC Mode (uc=True) лучше оставлять None, чтобы UA строго совпадал с 
        # отпечатками самого браузера, иначе антифрод заметит несоответствие.
        agent=user_agent,
        
        # Отключение Content-Security-Policy (CSP) на целевом сайте.
        # Варианты: True / False.
        # Если True, вы сможете выполнять свои JS-скрипты на странице (через driver.execute_script),
        # даже если сайт это жестко блокирует своими заголовками безопасности.
        disable_csp=True,

        # --- НАСТРОЙКИ СЕТИ И ПРОИЗВОДИТЕЛЬНОСТИ ---
        
        # Стратегия ожидания загрузки страницы.
        # Варианты:
        #   "normal" - ждет загрузки всего (HTML, картинки, стили, скрипты). Самый медленный.
        #   "eager"  - ждет только загрузки DOM (событие DOMContentLoaded). Оптимально для парсинга!
        #   "none"   - вообще не ждет, отдает управление скрипту сразу после получения первых байтов.
        page_load_strategy="eager",
        
        # Прокси-сервер.
        # Форматы: "ip:port" или "user:pass@ip:port".
        # Если None - запрос идет напрямую.
        proxy=proxy_str,
        
        # Язык браузера.
        # Варианты: "en", "ru", "en-US" и т.д.
        # Для зарубежных сайтов лучше ставить "en" или "en-US", чтобы не выделяться.
        locale_code="en",
        
        # --- СЕРВЕРНЫЕ И СИСТЕМНЫЕ НАСТРОЙКИ ---
        
        # Отключение песочницы (sandbox) браузера.
        # Варианты: True / False.
        # Обязательно ставьте True, если запускаете парсер на Linux (VPS, Docker) под root-пользователем,
        # иначе Chrome просто не запустится (выдаст ошибку). На Windows/Mac можно False.
        no_sandbox=False,
        
        # Отключение аппаратного ускорения (GPU).
        # Варианты: True / False.
        # Полезно ставить True на слабых серверах без видеокарт (VPS), чтобы избежать крашей.
        disable_gpu=False,
    )

    # --- ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ ПОСЛЕ ИНИЦИАЛИЗАЦИИ ---
    
    # Установка размера окна.
    # Если headless=False, слишком маленькое окно или его отсутствие может выдать бота.
    driver.set_window_size(1920, 1080)
    
    # Неявное ожидание появления элементов на странице (в секундах).
    # Ставим 0, так как в современном коде лучше использовать явные ожидания (WebDriverWait) 
    # или встроенные методы SeleniumBase (driver.wait_for_element).
    driver.implicitly_wait(0)
    
    # Максимальное время на загрузку страницы (прервет, если сайт висит).
    driver.set_page_load_timeout(60)

    return driver

# =============================================================================
# Извлечение текста элемента
# =============================================================================

from selenium.common.exceptions import TimeoutException

def get_text_by_css(
    driver,
    css_selector: str,
    timeout: int = 10,
    default: str | None = None,
    strip: bool = True,
    debug: bool = False,
) -> str | None:
    """
    Возвращает текст первого видимого элемента, найденного по CSS-селектору.

    Функция рассчитана на работу с SeleniumBase Driver, где implicit wait
    обычно отключен, а ожидание делается через встроенные explicit wait-методы.

    Параметры:
        driver:
            Экземпляр SeleniumBase Driver.

        css_selector:
            CSS-селектор искомого элемента.

        timeout:
            Максимальное время ожидания элемента в секундах.

        default:
            Значение, которое будет возвращено, если элемент не найден
            или текст получить не удалось.

        strip:
            Если True, убирает пробелы и переводы строк по краям текста.

        debug:
            Если True, печатает диагностические сообщения в консоль.

    Возвращает:
        str | None:
            Текст элемента, либо default, если элемент не найден
            или произошла ошибка.

    Пример:
        company_name = get_text_by_css(
            driver,
            ".company__title",
            timeout=10,
            debug=True,
        )
    """
    try:
        element = driver.wait_for_element_visible(css_selector, timeout=timeout)
        text = element.text

        if text is None:
            return default

        if strip:
            text = text.strip()

        return text if text else default

    except TimeoutException:
        if debug:
            print(f"[get_text_by_css] Элемент не найден за {timeout} сек.: {css_selector}")
        return default

    except Exception as e:
        if debug:
            print(f"[get_text_by_css] Ошибка для селектора {css_selector}: {e}")
        return default

# =============================================================================
# Извлечение поисковой выдачи (2GIS)
# =============================================================================

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_visible_elements(driver, selector="._1kf6gff", timeout=10):
    """
    Надежный поиск элементов для сложных SPA (2GIS).
    Использует нативный WebDriverWait + presence (не visible).
    """
    try:
        # Ждем появления в DOM (не обязательно на экране)
        wait = WebDriverWait(driver, timeout)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        
        # Собираем все найденные элементы
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        
        return elements
        
    except Exception as e:
        print(f"❌ Не удалось найти '{selector}': {type(e).__name__}")
        return []

#### Извлечение координат

import re
from urllib.parse import unquote

def _extract_coords(url_string: str) -> tuple | None:
    """
    [Подфункция] Извлекает координаты (долгота, широта) из 2GIS URL.
    Ищет паттерн вида '|lat,lon' и возвращает (lon, lat).
    """
    if not url_string:
        return None

    decoded_url = unquote(url_string)
    
    # Ищем координаты после символа пайпа '|'
    match = re.search(r'\|([\d.]+),([\d.]+)', decoded_url)
    if match:
        lat, lon = map(float, match.groups())
        return (lon, lat)  # Обычно в геоаналитике принят порядок (X, Y) -> (lon, lat)
        
    return None

def get_place_coords(
    driver, 
    route_btn_css: str = "a._1pl504b", 
    timeout: int = 10,
    debug: bool = False
) -> dict | None:
    """
    Снимает информацию с карточки места (2GIS).
    Кликает по элементу, дожидается кнопки маршрута и собирает текст.

    Параметры:
    - driver: SeleniumBase Driver.
    - card_element: WebElement самой карточки (которую нужно кликнуть).
    - route_btn_css: CSS-селектор кнопки "Проехать".
    - timeout: Сколько секунд ждать появления кнопки маршрута.
    - debug: Печатать ли ошибки в консоль.

    Возвращает:
    - Словарь с данными компании или None при ошибке.
    """
    try:
        # 1. Ждем появления кнопки маршрута (вместо жесткого time.sleep)
        # Это умное ожидание SeleniumBase: пойдет дальше, как только кнопка появится
        route_link_element = driver.wait_for_element(route_btn_css, timeout=timeout)

        # 2. Достаем ссылку пути
        href = route_link_element.get_attribute("href")

        # 3. Достаем координаты через подфункцию
        coords_tuple = _extract_coords(href)

        return href, coords_tuple

    except Exception as e:
        if debug:
            print(f"[get_company_info] Ошибка обработки карточки: {e}")
        return None, None

# =============================================================================
# Извлечение остальной информации о месте
# =============================================================================

def get_main_attrs(
    element,
    coords_tuple=None,
    url=None,
) -> dict:
    """
    Извлекает основные атрибуты карточки из element.text
    c привязкой к индексам строк.

    Параметры:
    - element: WebElement карточки.
    - coords_tuple: координаты места, если уже были извлечены ранее.
    - url: URL карточки / компании, если уже был извлечен ранее.

    Возвращает:
    - dict с основными и сырыми полями карточки.
    """
    try:
        element_text_list = [
            line.strip()
            for line in element.text.split("\n")
            if line.strip()
        ]

        company = element_text_list[0] if len(element_text_list) > 0 else None
        category = element_text_list[1] if len(element_text_list) > 1 else None
        rating = element_text_list[2] if len(element_text_list) > 2 else None
        reviews = element_text_list[3] if len(element_text_list) > 3 else None
        address = element_text_list[4] if len(element_text_list) > 4 else None
        extra_1 = element_text_list[5] if len(element_text_list) > 5 else None
        extra_2 = element_text_list[6] if len(element_text_list) > 6 else None
        extra_3 = element_text_list[7] if len(element_text_list) > 7 else None
        extra_4 = element_text_list[8] if len(element_text_list) > 8 else None

        return {
            "Company": company,
            "Category": category,
            "Rating": rating,
            "Reviews": reviews,
            "Address": address,
            "Extra_1": extra_1,
            "Extra_2": extra_2,
            "Extra_3": extra_3,
            "Extra_4": extra_4,
            "Coords": coords_tuple,
            "URL": url,
            "RawText": element.text,
            "RawLines": element_text_list,
        }

    except Exception as e:
        print(f"[get_main_attrs] Ошибка извлечения атрибутов: {e}")
        return {
            "Company": None, "Category": None, "Rating": None, "Reviews": None, "Address": None,
            "Extra_1": None, "Extra_2": None, "Extra_3": None, "Extra_4": None, 
            "Coords": coords_tuple, "URL": url, "RawText": None, "RawLines": [],
        }
        
# =============================================================================
# Переход на следующую страницу
# =============================================================================

from time import sleep

def turn_page(driver, class_name: str = '_n5hmn94', forward: bool = True, debug=False) -> bool:
    """
    Переключает страницу пагинации в 2ГИС.

    Находит кнопки навигации по классу и кликает на следующую
    или предыдущую в зависимости от флага forward.

    Args:
        driver:     Экземпляр SeleniumBase driver.
        class_name: CSS-класс кнопок пагинации.
        forward:    True — следующая страница, False — предыдущая.

    Returns:
        True при успешном переходе, False при ошибке.
    """
    try:
        elements = driver.find_elements(f'.{class_name}')
        if not elements:
            return False

        target = elements[-1] if forward else elements[-2]
        target.click()
        sleep(0.7)

        return True

    except Exception as e:
        if debug:
            print(f"[get_company_info] Ошибка обработки карточки: {e}")
        return False