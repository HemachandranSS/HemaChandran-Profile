from datetime import datetime
import os
import sys
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


DEFAULT_TASK_TYPE = "12"
DEFAULT_STATUS = "2"
DEFAULT_START_TIME = "12:00:00"
DEFAULT_END_TIME = "21:00:00"
POST_SUBMIT_WAIT_SECONDS = 2
ALREADY_UPDATED_KEYWORDS = (
    "already update",
    "already updated",
    "already exist",
    "already submitted",
    "duplicate",
)
SKIP_VALIDATION_MESSAGES = (
    "timesheet hour should not exceed 12 hours",
)

TIMESHEET_2026_ENTRIES = [
  {"date": "01/06/2026", "task": "TEST", "description": "Test"},
  {"date": "02/06/2026", "task": "TEST", "description": "Test"},
  {"date": "03/06/2026", "task": "TEST", "description": "Test"},
  {"date": "04/06/2026", "task": "TEST", "description": "Test"},
  {"date": "05/06/2026", "task": "TEST", "description": "Test"},
  {"date": "08/06/2026", "task": "TEST", "description": "Test"},
  {"date": "09/06/2026", "task": "TEST", "description": "Test"},
  {"date": "10/06/2026", "task": "TEST", "description": "Test"},
  {"date": "11/06/2026", "task": "TEST", "description": "Test"},
  {"date": "12/06/2026", "task": "TEST", "description": "Test"},
  {"date": "15/06/2026", "task": "TEST", "description": "Test"},
  {"date": "16/06/2026", "task": "TEST", "description": "Test"},
  {"date": "17/06/2026", "task": "TEST", "description": "Test"},
  {"date": "18/06/2026", "task": "TEST", "description": "Test"},
  {"date": "19/06/2026", "task": "TEST", "description": "Test"},
  {"date": "22/06/2026", "task": "TEST", "description": "Test"},
  {"date": "23/06/2026", "task": "TEST", "description": "Test"},
  {"date": "24/06/2026", "task": "TEST", "description": "Test"},
  {"date": "25/06/2026", "task": "TEST", "description": "Test"},
  {"date": "26/06/2026", "task": "TEST", "description": "Test"},
  {"date": "29/06/2026", "task": "TEST", "description": "Test"},
  {"date": "30/06/2026", "task": "TEST", "description": "Test"}
]



def trigger_change(driver, element):
    driver.execute_script(
        """
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
        """,
        element,
    )


def set_text_input(driver, element, value):
    driver.execute_script(
        """
        const input = arguments[0];
        const fieldValue = arguments[1];
        input.focus();
        input.value = '';
        input.value = fieldValue;
        if (window.jQuery) {
            window.jQuery(input).val(fieldValue).trigger('input').trigger('change').trigger('blur');
        }
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        input.dispatchEvent(new Event('blur', { bubbles: true }));
        """,
        element,
        value,
    )


def set_date_input(driver, date_input, value):
    driver.execute_script(
        """
        const input = arguments[0];
        const dateValue = arguments[1];
        input.removeAttribute('readonly');
        input.value = dateValue;
        if (window.jQuery) {
            window.jQuery(input).val(dateValue).trigger('change').trigger('blur');
        }
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        input.dispatchEvent(new Event('blur', { bubbles: true }));
        """,
        date_input,
        value,
    )


def set_description(driver, textarea, value):
    driver.execute_script(
        """
        const input = arguments[0];
        const content = arguments[1];
        input.value = content;
        if (window.CKEDITOR && CKEDITOR.instances && CKEDITOR.instances.pagecontent) {
            CKEDITOR.instances.pagecontent.setData(content);
            CKEDITOR.instances.pagecontent.updateElement();
        }
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        """,
        textarea,
        value,
    )


def is_already_updated_message(message):
    normalized_message = message.strip().lower()
    return any(keyword in normalized_message for keyword in ALREADY_UPDATED_KEYWORDS)


def get_element_text(driver, element_id):
    for element in driver.find_elements(By.ID, element_id):
        text = (element.get_attribute("textContent") or element.text or "").strip()
        if text:
            return " ".join(text.split())
    return ""


def get_skip_validation_message(driver):
    for alert_id in ("hours_alert", "hours1_alert", "hours3_alert"):
        alert_text = get_element_text(driver, alert_id)
        normalized_text = alert_text.lower()
        if any(message in normalized_text for message in SKIP_VALIDATION_MESSAGES):
            return alert_text
    return ""


def select_value(driver, wait, element_id, value):
    dropdown = wait.until(EC.presence_of_element_located((By.ID, element_id)))
    driver.execute_script(
        """
        const select = arguments[0];
        const selectedValue = arguments[1];
        select.value = selectedValue;
        if (window.jQuery) {
            window.jQuery(select).val(selectedValue).trigger('change').trigger('blur');
        }
        select.dispatchEvent(new Event('change', { bubbles: true }));
        select.dispatchEvent(new Event('blur', { bubbles: true }));
        """,
        dropdown,
        value,
    )
    wait.until(lambda d: d.find_element(By.ID, element_id).get_attribute("value") == value)
    return dropdown


def wait_for_time_validation(driver, wait, hour_id, minute_id):
    def validation_complete(d):
        hour_value = d.find_element(By.ID, hour_id).get_attribute("value").strip()
        minute_value = d.find_element(By.ID, minute_id).get_attribute("value").strip()
        if not hour_value or not minute_value:
            return False

        if d.find_elements(By.ID, "loader"):
            return False

        validation_message = get_skip_validation_message(d)
        submit_disabled = d.find_element(By.ID, "add_ts").get_attribute("disabled") is not None
        return bool(validation_message) or not submit_disabled

    wait.until(validation_complete)


def normalize_date(date_value):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_value.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {date_value}")


def build_entries():
    if len(sys.argv) >= 2:
        entry_date = sys.argv[3] if len(sys.argv) > 3 else datetime.now().strftime("%Y-%m-%d")
        return [{
            "date": normalize_date(entry_date),
            "task": sys.argv[1],
            "description": sys.argv[2] if len(sys.argv) > 2 else "",
        }]
    return [
        {
            **entry,
            "date": normalize_date(entry["date"]),
        }
        for entry in TIMESHEET_2026_ENTRIES
    ]


def login(driver, wait):
    driver.get("https://mycipl.in/")

    username = wait.until(EC.presence_of_element_located((By.ID, "login_user")))
    password = wait.until(EC.presence_of_element_located((By.ID, "login_pwd")))

    username.send_keys(os.getenv("MYCIPL_USERNAME", "hemachandran@colanonline.com"))
    password.send_keys(os.getenv("MYCIPL_PASSWORD", "Nxmoc9$"))

    wait.until(EC.element_to_be_clickable((By.ID, "login_submit"))).click()


def open_manual_timesheet_form(driver, wait):
    wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'module=ts')]"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[2]/ul/li[3]/a"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "//table//tr[6]/td[6]/a[1]"))).click()
    wait.until(EC.presence_of_element_located((By.ID, "add_tab")))
    return driver.current_url


def open_saved_form(driver, wait, form_url):
    driver.get(form_url)
    wait.until(EC.presence_of_element_located((By.ID, "add_tab")))


def fill_billable_timesheet(driver, wait, entry):
    select_value(driver, wait, "mile", "General_Bill")
    wait.until(lambda d: d.find_element(By.ID, "billable_form").is_displayed())
    wait.until(lambda d: d.find_element(By.ID, "billable_genform").is_displayed())

    task_input = wait.until(EC.presence_of_element_located((By.ID, "task1")))
    set_text_input(driver, task_input, entry["task"])
    wait.until(lambda d: d.find_element(By.ID, "task1").get_attribute("value").strip() == entry["task"])

    select_value(driver, wait, "type", DEFAULT_TASK_TYPE)

    date_input = wait.until(EC.presence_of_element_located((By.ID, "date1")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", date_input)
    set_date_input(driver, date_input, entry["date"])
    wait.until(lambda d: d.find_element(By.ID, "date1").get_attribute("value").strip() == entry["date"])

    if entry["description"]:
        description_input = wait.until(EC.presence_of_element_located((By.ID, "pagecontent")))
        set_description(driver, description_input, entry["description"])
        wait.until(lambda d: entry["description"] in d.find_element(By.ID, "pagecontent").get_attribute("value"))

    select_value(driver, wait, "status1", DEFAULT_STATUS)
    select_value(driver, wait, "tms_sttime", DEFAULT_START_TIME)
    select_value(driver, wait, "tms_endtime", DEFAULT_END_TIME)

    wait_for_time_validation(driver, wait, "hr", "mins")

    validation_message = get_skip_validation_message(driver)
    if validation_message:
        return False, validation_message

    submit_button = wait.until(EC.element_to_be_clickable((By.ID, "add_ts")))
    driver.execute_script("arguments[0].click();", submit_button)

    time.sleep(1)

    validation_message = get_skip_validation_message(driver)
    if validation_message:
        return False, validation_message

    try:
        alert = WebDriverWait(driver, 3).until(EC.alert_is_present())
        alert_text = alert.text.strip()
        alert.accept()
        if is_already_updated_message(alert_text):
            return False, alert_text
        raise RuntimeError(alert_text or "Unexpected submit alert")
    except TimeoutException:
        return True, ""


def run():
    entries = build_entries()

    options = Options()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    wait = WebDriverWait(driver, 20)

    try:
        login(driver, wait)
        form_url = open_manual_timesheet_form(driver, wait)

        for index, entry in enumerate(entries, start=1):
            try:
                if index > 1:
                    open_saved_form(driver, wait, form_url)

                submitted, message = fill_billable_timesheet(driver, wait, entry)
                if submitted:
                    print(f"[{index}/{len(entries)}] Submitted {entry['date']} - {entry['task']}")
                else:
                    print(f"[{index}/{len(entries)}] Skipped {entry['date']} - {entry['task']}: {message}")
                time.sleep(POST_SUBMIT_WAIT_SECONDS)
            except Exception as exc:
                print(f"[{index}/{len(entries)}] Skipped {entry['date']} - {entry['task']}: {exc}")
                continue
    finally:
        driver.quit()


if __name__ == "__main__":
    run()
