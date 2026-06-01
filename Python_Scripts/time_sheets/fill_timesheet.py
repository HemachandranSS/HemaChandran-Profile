from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import os
import sys
import time

DEFAULT_TASK_TYPE = "12"
DEFAULT_STATUS = "2"
DEFAULT_START_TIME = "12:00:00"
DEFAULT_END_TIME = "21:00:00"


def test_login():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python fill_timesheet.py <task> [description]")

    options = Options()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    wait = WebDriverWait(driver, 20)

    try:
        driver.get("https://mycipl.in/")

        username = wait.until(EC.presence_of_element_located((By.ID, "login_user")))
        password = wait.until(EC.presence_of_element_located((By.ID, "login_pwd")))

        username.send_keys(os.getenv("MYCIPL_USERNAME", "hemachandran@colanonline.com"))
        password.send_keys(os.getenv("MYCIPL_PASSWORD", "Nxmoc9$"))

        wait.until(EC.element_to_be_clickable((By.ID, "login_submit"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'module=ts')]"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[2]/ul/li[3]/a"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//table//tr[6]/td[6]/a[1]"))).click()

        milestone_dropdown = wait.until(EC.presence_of_element_located((By.ID, "mile")))
        Select(milestone_dropdown).select_by_value("General_Bill")
        wait.until(lambda d: d.find_element(By.ID, "billable_form").is_displayed())
        wait.until(lambda d: d.find_element(By.ID, "billable_genform").is_displayed())

        task_value = sys.argv[1]
        description_value = sys.argv[2] if len(sys.argv) > 2 else ""
        wait.until(EC.presence_of_element_located((By.ID, "task1"))).send_keys(task_value)

        work_type_dropdown = wait.until(EC.presence_of_element_located((By.ID, "type")))
        Select(work_type_dropdown).select_by_value(DEFAULT_TASK_TYPE)

        today_str = datetime.now().strftime("%Y-%m-%d")
        date_input = wait.until(EC.presence_of_element_located((By.ID, "date1")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", date_input)
        driver.execute_script(
            """
            const input = arguments[0];
            const value = arguments[1];
            input.removeAttribute('readonly');
            input.value = value;
            if (window.jQuery) {
                window.jQuery(input).val(value).trigger('change').trigger('blur');
            }
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
            input.dispatchEvent(new Event('blur', { bubbles: true }));
            """,
            date_input,
            today_str,
        )
        wait.until(lambda d: date_input.get_attribute("value").strip() == today_str)

        if description_value:
            description_input = wait.until(EC.presence_of_element_located((By.ID, "pagecontent")))
            driver.execute_script(
                """
                const textarea = arguments[0];
                const value = arguments[1];
                textarea.value = value;
                if (window.CKEDITOR && CKEDITOR.instances && CKEDITOR.instances.pagecontent) {
                    CKEDITOR.instances.pagecontent.setData(value);
                    CKEDITOR.instances.pagecontent.updateElement();
                }
                textarea.dispatchEvent(new Event('input', { bubbles: true }));
                textarea.dispatchEvent(new Event('change', { bubbles: true }));
                """,
                description_input,
                description_value,
            )

        status_dropdown = wait.until(EC.presence_of_element_located((By.ID, "status1")))
        Select(status_dropdown).select_by_value(DEFAULT_STATUS)

        start_time_dropdown = wait.until(EC.presence_of_element_located((By.ID, "tms_sttime")))
        Select(start_time_dropdown).select_by_value(DEFAULT_START_TIME)
        driver.execute_script(
            "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
            start_time_dropdown,
        )

        end_time_dropdown = wait.until(EC.presence_of_element_located((By.ID, "tms_endtime")))
        Select(end_time_dropdown).select_by_value(DEFAULT_END_TIME)
        driver.execute_script(
            "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
            end_time_dropdown,
        )

        wait.until(lambda d: d.find_element(By.ID, "hr").get_attribute("value").strip() != "")
        wait.until(lambda d: d.find_element(By.ID, "mins").get_attribute("value").strip() != "")
        wait.until(lambda d: d.find_element(By.ID, "add_ts").get_attribute("disabled") is None)

        submit_button = wait.until(EC.element_to_be_clickable((By.ID, "add_ts")))
        driver.execute_script("arguments[0].click();", submit_button)

        print(f"Selected today's date ({today_str}) and submitted the form")
        time.sleep(5)
    finally:
        driver.quit()


if __name__ == "__main__":
    test_login()
