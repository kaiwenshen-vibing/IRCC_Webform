import re
import time

from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://secure.cic.gc.ca/ClientContact/en/Application/Form/72")
    time.sleep(2)
    page.get_by_role("radio", name="I'm the principal applicant").check()
    page.get_by_role("button", name="Continue to form").click()
    page.get_by_role("textbox", name="* First name(s) (also known").click()
    page.get_by_role("textbox", name="* First name(s) (also known").press("CapsLock")
    page.get_by_role("textbox", name="* First name(s) (also known").fill("K")
    page.get_by_role("textbox", name="* First name(s) (also known").press("CapsLock")
    page.get_by_role("textbox", name="* First name(s) (also known").fill("Kaiwen")
    page.get_by_role("textbox", name="* Last name(s) (also known as").click()
    page.get_by_role("textbox", name="* Last name(s) (also known as").press("CapsLock")
    page.get_by_role("textbox", name="* Last name(s) (also known as").fill("S")
    page.get_by_role("textbox", name="* Last name(s) (also known as").press("CapsLock")
    page.get_by_role("textbox", name="* Last name(s) (also known as").fill("Shen")
    page.get_by_role("textbox", name="* Email address").click()
    page.get_by_role("textbox", name="* Email address").fill("kevinskw@outlook.com")
    page.get_by_role("textbox", name="* Confirm your email address").click()
    page.get_by_role("textbox", name="* Confirm your email address").fill("kevinskw@outlook.com")
    page.get_by_label("Year (required)").select_option("2000")
    page.get_by_label("Month (required)").select_option("03")
    page.get_by_label("Day (required)").select_option("30")
    page.get_by_label("Country or territory of birth").select_option("1852")
    page.get_by_role("textbox", name="* What’s your application").click()
    page.get_by_role("textbox", name="* What’s your application").press("CapsLock")
    page.get_by_role("textbox", name="* What’s your application").fill("W")
    page.get_by_role("textbox", name="* What’s your application").press("CapsLock")
    page.get_by_role("textbox", name="* What’s your application").fill("W308468626")
    page.get_by_label("What did you apply for? (").select_option("2")
    page.get_by_label("What application did you").select_option("14")
    page.get_by_role("textbox", name="* What’s your Unique Client").click()
    page.get_by_role("textbox", name="* What’s your Unique Client").fill("1116762582")
    page.get_by_label("What country or territory").select_option("1842")
    page.get_by_label("What nationality is listed on").select_option("1852")
    page.get_by_role("textbox", name="* What is your passport").click()
    page.get_by_role("textbox", name="* What is your passport").press("CapsLock")
    page.get_by_role("textbox", name="* What is your passport").fill("EB7769111")
    page.get_by_label("What is the issuing country/").select_option("1852")
    page.get_by_text("Online", exact=True).click()
    page.get_by_label("Did we ask you to add the").select_option("63")
    page.get_by_role("textbox", name="* Please explain in the text").click()
    page.get_by_role("textbox", name="* Please explain in the text").fill(
        "I have been incorrectly refused PGWP, please help, this is a request for reconsideration. I have a full time job working for Canadian Pension Plan, detail in the documents. I have submitted this before but have not received response yet.")
    with page.expect_file_chooser() as fc_info:
        page.get_by_role("button", name="Choose File").click()
    file_chooser = fc_info.value
    file_chooser.set_files("./file_src/reconsideration_request.pdf")
    page.get_by_role("button", name="Upload").click()

    with page.expect_file_chooser() as fc_info:
        page.get_by_role("button", name="Choose File").click()
    file_chooser = fc_info.value
    file_chooser.set_files("./file_src/ielts.pdf")
    page.get_by_role("button", name="Upload").click()

    page.get_by_role("checkbox", name="I’ve read and understand the").check()
    page.get_by_role("button", name="Review your request").click()
    page.get_by_role("button", name="Submit your request").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
