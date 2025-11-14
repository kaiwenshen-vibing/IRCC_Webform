import random


def human_move_mouse(page):
    width = page.viewport_size["width"]
    height = page.viewport_size["height"]

    for _ in range(random.randint(5, 10)):
        x = random.randint(0, width)
        y = random.randint(0, height)
        page.mouse.move(x, y, steps=random.randint(10, 25))
        page.wait_for_timeout(random.randint(30, 120))


def human_scroll(page):
    for _ in range(random.randint(2,4)):
        page.mouse.wheel(0, random.randint(200, 600))
        page.wait_for_timeout(random.randint(200, 500))


def human_click(page, selector):
    el = page.locator(selector)
    box = el.bounding_box()

    x = box["x"] + box["width"]/2 + random.randint(-3,3)
    y = box["y"] + box["height"]/2 + random.randint(-3,3)

    # Realistic approach
    page.mouse.move(x, y, steps=random.randint(15, 30))
    page.wait_for_timeout(random.randint(100, 250))
    page.mouse.click(x, y)

def human_select(page,click_selector,txt):
    # open the dropdown
    page.click(click_selector)

    # # scroll the dropdown container (not the whole page)
    # for _ in range(10):
    #     page.mouse.wheel(0, 300)
    #     page.wait_for_timeout(10)

    option_selector = f"{click_selector} >> option[value='{txt}']"
    option_el = page.locator(option_selector)
    option_el.click()