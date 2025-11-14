import random


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

TIMEZONES = [
    "America/Toronto",
    "America/Vancouver",
    "America/Edmonton",
    "America/New_York",
]

LOCALES = ["en-CA", "en-US", "fr-CA"]

VIEWPORTS = [
    (1920, 1080),
    (1600, 900),
    (1536, 864),
    (1440, 900),
    (1366, 768),
    (1280, 720),
]

COLOR_SCHEMES = ["light", "dark"]


def _resolve_locator(page, target):
    if isinstance(target, str):
        return page.locator(target)
    return target


def human_pause(page, min_ms=180, max_ms=480):
    page.wait_for_timeout(random.randint(min_ms, max_ms))


def generate_browser_fingerprint():
    base_width, base_height = random.choice(VIEWPORTS)
    viewport = {
        "width": base_width + random.randint(-60, 30),
        "height": base_height + random.randint(-60, 20),
    }
    is_mobile = random.random() < 0.15
    fingerprint = {
        "user_agent": random.choice(USER_AGENTS),
        "locale": random.choice(LOCALES),
        "timezone": random.choice(TIMEZONES),
        "color_scheme": random.choice(COLOR_SCHEMES),
        "viewport": viewport,
        "device_scale_factor": 1.0 if not is_mobile else random.choice([2.0, 2.5]),
        "is_mobile": is_mobile,
        "has_touch": is_mobile or random.random() < 0.25,
        "accept_language": random.choice(
            ["en-CA,en;q=0.9", "en-US,en;q=0.8", "fr-CA,fr;q=0.8,en;q=0.6"]
        ),
    }
    return fingerprint


def create_human_context(playwright, *, headless=False):
    fingerprint = generate_browser_fingerprint()
    browser = playwright.chromium.launch(
        headless=headless,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--no-default-browser-check",
        ],
    )
    context = browser.new_context(
        viewport=fingerprint["viewport"],
        user_agent=fingerprint["user_agent"],
        locale=fingerprint["locale"],
        timezone_id=fingerprint["timezone"],
        color_scheme=fingerprint["color_scheme"],
        device_scale_factor=fingerprint["device_scale_factor"],
        is_mobile=fingerprint["is_mobile"],
        has_touch=fingerprint["has_touch"],
    )
    context.set_extra_http_headers(
        {"Accept-Language": fingerprint["accept_language"], "DNT": "1"}
    )
    return browser, context, fingerprint


def human_move_mouse(page):
    viewport = page.viewport_size or {"width": 1280, "height": 720}
    width = viewport["width"]
    height = viewport["height"]

    for _ in range(random.randint(6, 12)):
        x = random.randint(0, width)
        y = random.randint(0, height)
        page.mouse.move(x, y, steps=random.randint(12, 30))
        human_pause(page, 35, 140)


def human_scroll(page):
    for _ in range(random.randint(2, 4)):
        page.mouse.wheel(0, random.randint(200, 600))
        human_pause(page, 220, 520)


def human_click(page, target):
    el = _resolve_locator(page, target)
    el.wait_for(state="visible")
    el.scroll_into_view_if_needed()
    box = el.bounding_box()
    if not box:
        el.click()
        return

    x = box["x"] + box["width"] / 2 + random.randint(-4, 4)
    y = box["y"] + box["height"] / 2 + random.randint(-4, 4)

    page.mouse.move(
        x + random.randint(-8, 8),
        y + random.randint(-8, 8),
        steps=random.randint(15, 32),
    )
    human_pause(page, 110, 260)
    page.mouse.click(x, y, delay=random.randint(30, 90))
    human_pause(page, 130, 320)


def human_type(page, target, text, min_delay=25, max_delay=95):
    el = _resolve_locator(page, target)
    el.wait_for(state="visible")
    el.click()
    el.press("Control+A")
    el.press("Backspace")

    for char in text:
        el.type(char, delay=random.randint(min_delay, max_delay))
        if random.random() < 0.08:
            el.press("Backspace")
            human_pause(page, 45, 110)
            el.type(char, delay=random.randint(min_delay, max_delay))
        if random.random() < 0.15:
            human_pause(page, 40, 140)
    human_pause(page, 140, 360)


def human_select(page, target, value):
    el = _resolve_locator(page, target)
    el.wait_for(state="visible")
    el.scroll_into_view_if_needed()
    human_click(page, el)
    human_pause(page, 120, 260)
    el.select_option(value)
    human_pause(page, 140, 300)
