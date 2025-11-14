from playwright.sync_api import Playwright, sync_playwright

from human_utils import (
    create_human_context,
    human_click,
    human_move_mouse,
    human_pause,
    human_scroll,
    human_select,
    human_type,
)

FORM_VALUES = {
    "first_name": "Kaiwen",
    "last_name": "Shen",
    "email": "kevinskw@outlook.com",
    "dob": {"year": "2000", "month": "03", "day": "30"},
    "country_of_birth": "1852",
    "application_number": "W308468626",
    "application_type": "2",
    "application_subcategory": "14",
    "uci": "1116762582",
    "country_of_residence": "1842",
    "nationality": "1852",
    "passport_number": "EB7769111",
    "passport_country": "1852",
    "request_reason": "63",
}

REQUEST_MESSAGE = (
    "I have been incorrectly refused PGWP, please help, this is a request for "
    "reconsideration. I have a full time job working for Canadian Pension Plan, "
    "detail in the documents. I have submitted this before but have not received "
    "response yet."
)

ATTACHMENTS = [
    "./file_src/reconsideration_request.pdf",
    "./file_src/ielts.pdf",
]


def load_form(page):
    page.goto("https://secure.cic.gc.ca/ClientContact/en/Application/Form/72", wait_until="domcontentloaded")
    human_pause(page, 650, 1200)
    human_move_mouse(page)
    human_click(page, page.get_by_role("radio", name="I'm the principal applicant"))
    human_pause(page, 280, 620)
    human_click(page, page.get_by_role("button", name="Continue to form"))
    page.wait_for_load_state("domcontentloaded")
    human_scroll(page)
    human_move_mouse(page)


def fill_personal_information(page):
    human_type(page, page.get_by_role("textbox", name="* First name(s) (also known"), FORM_VALUES["first_name"])
    human_type(page, page.get_by_role("textbox", name="* Last name(s) (also known as"), FORM_VALUES["last_name"])
    human_type(page, page.get_by_role("textbox", name="* Email address"), FORM_VALUES["email"])
    human_type(page, page.get_by_role("textbox", name="* Confirm your email address"), FORM_VALUES["email"])

    human_select(page, page.get_by_label("Year (required)"), FORM_VALUES["dob"]["year"])
    human_select(page, page.get_by_label("Month (required)"), FORM_VALUES["dob"]["month"])
    human_select(page, page.get_by_label("Day (required)"), FORM_VALUES["dob"]["day"])
    human_select(page, page.get_by_label("Country or territory of birth"), FORM_VALUES["country_of_birth"])
    human_scroll(page)


def fill_application_details(page):
    human_type(page, page.get_by_role("textbox", name="* What’s your application"), FORM_VALUES["application_number"])
    human_select(page, page.get_by_label("What did you apply for? ("), FORM_VALUES["application_type"])
    human_select(page, page.get_by_label("What application did you"), FORM_VALUES["application_subcategory"])
    human_type(page, page.get_by_role("textbox", name="* What’s your Unique Client"), FORM_VALUES["uci"])
    human_select(page, page.get_by_label("What country or territory"), FORM_VALUES["country_of_residence"])
    human_select(page, page.get_by_label("What nationality is listed on"), FORM_VALUES["nationality"])
    human_type(page, page.get_by_role("textbox", name="* What is your passport"), FORM_VALUES["passport_number"])
    human_select(page, page.get_by_label("What is the issuing country/"), FORM_VALUES["passport_country"])

    human_click(page, page.get_by_text("Online", exact=True))
    human_select(page, page.get_by_label("Did we ask you to add the"), FORM_VALUES["request_reason"])
    human_scroll(page)
    human_type(page, page.get_by_role("textbox", name="* Please explain in the text"), REQUEST_MESSAGE, min_delay=18, max_delay=70)


def upload_supporting_documents(page):
    upload_button = page.get_by_role("button", name="Upload")
    choose_button = page.get_by_role("button", name="Choose File")

    for file_path in ATTACHMENTS:
        with page.expect_file_chooser() as fc_info:
            human_click(page, choose_button)
        file_chooser = fc_info.value
        file_chooser.set_files(file_path)
        human_pause(page, 320, 640)
        human_click(page, upload_button)
        human_pause(page, 360, 720)


def finalize_submission(page):
    human_scroll(page)
    human_click(page, page.get_by_role("checkbox", name="I’ve read and understand the"))
    human_pause(page, 320, 620)
    human_click(page, page.get_by_role("button", name="Review your request"))
    human_move_mouse(page)
    human_pause(page, 1200, 2000)
    human_click(page, page.get_by_role("button", name="Submit your request"))


def run(playwright: Playwright) -> None:
    browser, context, fingerprint = create_human_context(playwright, headless=False)
    page = context.new_page()
    print(
        "Using fingerprint:",
        fingerprint["user_agent"],
        fingerprint["locale"],
        fingerprint["timezone"],
        fingerprint["viewport"],
    )

    load_form(page)
    fill_personal_information(page)
    fill_application_details(page)
    upload_supporting_documents(page)
    finalize_submission(page)

    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
