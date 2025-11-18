import argparse
import random
import time
from datetime import datetime, timedelta
from pathlib import Path

import yaml
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

CONFIG_PATH = Path(__file__).with_name("config.yaml")


def load_config(path: Path = CONFIG_PATH):
    with path.open("r", encoding="utf-8") as source:
        data = yaml.safe_load(source)
    if not isinstance(data, dict):
        raise ValueError(f"Configuration file {path} is invalid or empty.")
    return data


CONFIG = load_config()
FORM_VALUES = CONFIG["form_values"]
REQUEST_MESSAGE = CONFIG["request_message"]
ATTACHMENTS = CONFIG["attachments"]
PROFILE_CONFIG = CONFIG.get("profile", {})
USE_PERSISTENT_PROFILE = PROFILE_CONFIG.get("use_persistent_profile", False)
PERSISTENT_PROFILE_PATH = PROFILE_CONFIG.get("persistent_profile_path")


def load_form(page):
    # page.goto("https://secure.cic.gc.ca/ClientContact/en/Application/Form/72", wait_until="domcontentloaded")
    page.goto("https://secure.cic.gc.ca/ClientContact/en/Application/Form/69", wait_until="domcontentloaded")
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
    # human_select(page, page.get_by_label("Did we ask you to add the"), FORM_VALUES["request_reason"])
    human_scroll(page)
    # human_type(page, page.get_by_role("textbox", name="* Please explain in the text"), REQUEST_MESSAGE, min_delay=18, max_delay=70)
    human_type(page, page.get_by_role("textbox", name="* Please explain how we can help"), REQUEST_MESSAGE, min_delay=18, max_delay=70)


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
    with page.expect_navigation():
        # this wait is because IRCC webform needs time to process before actually send, background task is a js driven complier to compile all your answers
        human_click(page, page.get_by_role("button", name="Submit your request"))

def run(playwright: Playwright, *, use_persistent_profile: bool = USE_PERSISTENT_PROFILE) -> None:
    browser = None
    context = None
    fingerprint = None

    if use_persistent_profile:
        if not PERSISTENT_PROFILE_PATH:
            raise ValueError("Persistent profile path must be set in config.yaml.")
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=PERSISTENT_PROFILE_PATH,
            headless=False,
        )
        page = context.pages[0] if context.pages else context.new_page()
        print(f"Using persistent Chrome profile at {PERSISTENT_PROFILE_PATH}")
    else:
        browser, context, fingerprint = create_human_context(playwright, headless=False)
        page = context.new_page()
        print(
            "Using fingerprint:",
            fingerprint["user_agent"],
            fingerprint["locale"],
            fingerprint["timezone"],
            fingerprint["viewport"],
        )

    try:
        load_form(page)
        fill_personal_information(page)
        fill_application_details(page)
        # upload_supporting_documents(page)
        finalize_submission(page)
    finally:
        if context:
            context.close()
        if browser:
            browser.close()


def schedule_runs(
    playwright: Playwright,
    count: int,
    *,
    start_hour: int = 9,
    end_hour: int = 21,
    use_persistent_profile: bool = USE_PERSISTENT_PROFILE,
) -> None:
    if count <= 0:
        raise ValueError("Schedule count must be greater than zero.")
    if start_hour >= end_hour:
        raise ValueError("Start hour must be before end hour.")

    now = datetime.now()
    window_start = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
    window_end = now.replace(hour=end_hour, minute=0, second=0, microsecond=0)

    if now >= window_end:
        window_start += timedelta(days=1)
        window_end += timedelta(days=1)
    elif now > window_start:
        window_start = now

    window_seconds = (window_end - window_start).total_seconds()
    if window_seconds <= 0:
        raise ValueError("Unable to compute a valid scheduling window.")

    scheduled_times = sorted(
        window_start + timedelta(seconds=random.uniform(0, window_seconds))
        for _ in range(count)
    )

    for idx, target_time in enumerate(scheduled_times, start=1):
        wait_seconds = (target_time - datetime.now()).total_seconds()
        if wait_seconds > 0:
            minutes = wait_seconds / 60
            print(
                f"Run {idx}/{count} scheduled for {target_time:%Y-%m-%d %H:%M:%S}. "
                f"Waiting {minutes:.1f} minutes."
            )
            time.sleep(wait_seconds)
        else:
            print(
                f"Scheduled run {idx}/{count} time {target_time:%Y-%m-%d %H:%M:%S} "
                "has already passed, running immediately."
            )

        print(f"Starting run {idx}/{count} at {datetime.now():%Y-%m-%d %H:%M:%S}")
        run(playwright, use_persistent_profile=use_persistent_profile)


def parse_args():
    parser = argparse.ArgumentParser(description="Automate IRCC webform submissions.")
    parser.add_argument(
        "--schedule-count",
        type=int,
        default=0,
        help="Number of scheduled runs between 9am and 9pm (default: run immediately once).",
    )
    parser.add_argument(
        "--schedule-start-hour",
        type=int,
        default=9,
        help="Start hour for random scheduling window (default: 9).",
    )
    parser.add_argument(
        "--schedule-end-hour",
        type=int,
        default=21,
        help="End hour for random scheduling window (default: 21).",
    )
    parser.add_argument(
        "--persistent-profile",
        dest="use_persistent_profile",
        action=argparse.BooleanOptionalAction,
        default=USE_PERSISTENT_PROFILE,
        help="Toggle use of the persistent Chrome profile defined in config.yaml.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    with sync_playwright() as playwright:
        if args.schedule_count and args.schedule_count > 0:
            schedule_runs(
                playwright,
                args.schedule_count,
                start_hour=args.schedule_start_hour,
                end_hour=args.schedule_end_hour,
                use_persistent_profile=args.use_persistent_profile,
            )
        else:
            run(playwright, use_persistent_profile=args.use_persistent_profile)


if __name__ == "__main__":
    main()
