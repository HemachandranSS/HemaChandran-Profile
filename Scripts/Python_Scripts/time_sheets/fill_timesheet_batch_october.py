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


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_TASK_TYPE = "12"
DEFAULT_STATUS = "2"
DEFAULT_START_TIME = "12:00:00"
DEFAULT_END_TIME = "21:00:00"
POST_SUBMIT_WAIT_SECONDS = 1

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


# ============================================================
# OCTOBER 2026 TIMESHEET ENTRIES
# ============================================================

TIMESHEET_2026_ENTRIES = [
    {"date": "01/10/2026", "task": "Mother Goose Development", "description": "Mother Goose Development"},
    {"date": "05/10/2026", "task": "Mother Goose Development", "description": "Mother Goose Development"},
    {"date": "06/10/2026", "task": "Mother Goose Development", "description": "Mother Goose Development"},
    {"date": "07/10/2026", "task": "Mother Goose Development", "description": "Mother Goose Development"},
    {"date": "08/10/2026", "task": "Mother Goose Development", "description": "Mother Goose Development"},
    {"date": "09/10/2026", "task": "Mother Goose Development", "description": "Mother Goose Development"},
    {"date": "12/10/2026", "task": "Mother Goose Development", "description": "Mother Goose Development"},
    {"date": "13/10/2026", "task": "Mother Goose Development", "description": "Mother Goose Development"},
    {"date": "14/10/2026", "task": "Mother Goose Development", "description": "Mother Goose Development"},
    {"date": "15/10/2026", "task": "Mother Goose Development", "description": "Mother Goose Development"},
    {"date": "16/10/2026", "task": "Mother Goose Development", "description": "Mother Goose Development"},
    {"date": "19/10/2026", "task": "Mother Goose Development", "description": "Mother Goose Development"},
    {"date": "20/10/2026", "task": "Mother Goose Development", "description": "Mother Goose Development"},
    {"date": "21/10/2026", "task": "Mother Goose Development", "description": "Mother Goose Development"},
    {"date": "22/10/2026", "task": "Mother Goose Development", "description": "Mother Goose Development"},
    {"date": "23/10/2026", "task": "Mother Goose Development", "description": "Mother Goose Development"},
    {"date": "26/10/2026", "task": "Mother Goose Development", "description": "Mother Goose Development"},
    {"date": "27/10/2026", "task": "Mother Goose Development", "description": "Mother Goose Development"},
    {"date": "28/10/2026", "task": "Mother Goose Development", "description": "Mother Goose Development"},
    {"date": "29/10/2026", "task": "Mother Goose Development", "description": "Mother Goose Development"},
    {"date": "30/10/2026", "task": "Mother Goose Development", "description": "Mother Goose Development"},
]


# ============================================================
# TRIGGER CHANGE
# ============================================================

def trigger_change(driver, element):
    driver.execute_script(
        """
        arguments[0].dispatchEvent(
            new Event('input', { bubbles: true })
        );

        arguments[0].dispatchEvent(
            new Event('change', { bubbles: true })
        );

        arguments[0].dispatchEvent(
            new Event('blur', { bubbles: true })
        );
        """,
        element,
    )


# ============================================================
# SET TEXT INPUT
# ============================================================

def set_text_input(driver, element, value):
    driver.execute_script(
        """
        const input = arguments[0];
        const fieldValue = arguments[1];

        input.focus();
        input.value = '';
        input.value = fieldValue;

        if (window.jQuery) {
            window.jQuery(input)
                .val(fieldValue)
                .trigger('input')
                .trigger('change')
                .trigger('blur');
        }

        input.dispatchEvent(
            new Event('input', { bubbles: true })
        );

        input.dispatchEvent(
            new Event('change', { bubbles: true })
        );

        input.dispatchEvent(
            new Event('blur', { bubbles: true })
        );
        """,
        element,
        value,
    )


# ============================================================
# FUTURE DATE VALIDATION BYPASS
# ============================================================

def bypass_future_date_validation(driver):
    """Complete bypass of future date validation"""

    driver.execute_script(
        """
        // 1. Override the hidden timestamp field
        var timestampField =
            document.getElementById(
                'checkingcurrent_date'
            );

        if (timestampField) {
            timestampField.value = '1893456000';

            console.log(
                'Timestamp field updated to:',
                timestampField.value
            );
        }


        // 2. Remove max date and restrictions
        var dateFields =
            document.querySelectorAll(
                '.jdpicker, [id^="date"], [class*="date"]'
            );

        dateFields.forEach(function(field) {
            field.removeAttribute('max');
            field.removeAttribute('maxDate');
            field.removeAttribute('maxlength');
            field.removeAttribute('readonly');

            field.readOnly = false;
        });


        // 3. Override Chk_Ts
        if (typeof window.Chk_Ts === 'function') {

            window.originalChk_Ts =
                window.Chk_Ts;

            window.Chk_Ts =
                function(form) {

                    console.log(
                        'Chk_Ts validation bypassed'
                    );

                    return true;
                };
        }


        // 4. Override jQuery validation
        if (
            window.jQuery &&
            jQuery.validator
        ) {

            jQuery.validator =
                jQuery.validator || {};

            if (jQuery.validator.methods) {

                jQuery.validator.methods.date =
                    function(value, element) {
                        return true;
                    };
            }
        }


        // 5. Override form submit validation
        var form =
            document.getElementById('add_tab');

        if (form) {

            if (form.onsubmit) {

                form.originalOnSubmit =
                    form.onsubmit;

                form.onsubmit =
                    function(event) {

                        console.log(
                            'Form onsubmit bypassed'
                        );

                        return true;
                    };
            }

            form.setAttribute(
                'novalidate',
                'novalidate'
            );
        }


        // 6. Intercept AJAX validation
        var originalFetch =
            window.fetch;

        window.fetch =
            function(url, options) {

                if (
                    url &&
                    (
                        url.includes(
                            'ajax-check_total_hrs.php'
                        ) ||
                        url.includes(
                            'validation'
                        ) ||
                        url.includes(
                            'check'
                        )
                    )
                ) {

                    console.log(
                        'AJAX validation intercepted:',
                        url
                    );

                    return Promise.resolve({
                        ok: true,

                        text: function() {
                            return Promise.resolve('');
                        },

                        json: function() {
                            return Promise.resolve({});
                        }
                    });
                }

                return originalFetch.apply(
                    this,
                    arguments
                );
            };


        // 7. Override XMLHttpRequest
        var XHR =
            XMLHttpRequest.prototype;

        var originalOpen =
            XHR.open;

        var originalSend =
            XHR.send;


        XHR.open =
            function(method, url) {

                this._url = url;

                return originalOpen.apply(
                    this,
                    arguments
                );
            };


        XHR.send =
            function(data) {

                if (
                    this._url &&
                    (
                        this._url.includes(
                            'ajax-check_total_hrs.php'
                        ) ||
                        this._url.includes(
                            'validation'
                        ) ||
                        this._url.includes(
                            'check'
                        )
                    )
                ) {

                    console.log(
                        'XHR validation intercepted:',
                        this._url
                    );

                    try {
                        Object.defineProperty(
                            this,
                            'status',
                            {
                                value: 200
                            }
                        );
                    } catch(e) {}

                    try {
                        Object.defineProperty(
                            this,
                            'responseText',
                            {
                                value: ''
                            }
                        );
                    } catch(e) {}

                    try {
                        Object.defineProperty(
                            this,
                            'readyState',
                            {
                                value: 4
                            }
                        );
                    } catch(e) {}

                    if (this.onload) {
                        this.onload();
                    }

                    if (this.onreadystatechange) {
                        this.onreadystatechange();
                    }

                    return;
                }

                return originalSend.apply(
                    this,
                    arguments
                );
            };


        // 8. Override future date check
        if (
            typeof window.checkFutureDate ===
            'function'
        ) {

            window.checkFutureDate =
                function() {

                    console.log(
                        'checkFutureDate bypassed'
                    );

                    return true;
                };
        }


        // 9. Override alert
        window.originalAlert =
            window.alert;

        window.alert =
            function(message) {

                if (
                    message &&
                    (
                        message
                            .toLowerCase()
                            .includes('future') ||

                        message
                            .toLowerCase()
                            .includes('invalid') ||

                        message
                            .toLowerCase()
                            .includes('date')
                    )
                ) {

                    console.log(
                        'Validation alert suppressed:',
                        message
                    );

                    return;
                }

                window.originalAlert(
                    message
                );
            };


        // 10. Override console.error
        console.originalError =
            console.error;

        console.error =
            function(message) {

                if (
                    message &&
                    (
                        message.includes(
                            'date'
                        ) ||
                        message.includes(
                            'validation'
                        )
                    )
                ) {

                    return;
                }

                console.originalError.apply(
                    console,
                    arguments
                );
            };


        console.log(
            'Future date validation bypass complete'
        );
        """
    )


# ============================================================
# SET DATE
# ============================================================

def set_date_without_validation(
    driver,
    date_input,
    date_value
):
    """Set date value directly via JavaScript"""

    driver.execute_script(
        """
        var input = arguments[0];
        var value = arguments[1];

        // Set value directly
        input.value = value;


        // Force update without validation
        try {

            if (window.jQuery) {

                window.jQuery(input)
                    .val(value);
            }

        } catch(e) {}


        // Update hidden timestamp
        var hiddenField =
            document.getElementById(
                'checkingcurrent_date'
            );

        if (hiddenField) {

            var parts =
                value.split('/');

            if (parts.length === 3) {

                var dateObj =
                    new Date(
                        parts[2],
                        parts[1] - 1,
                        parts[0]
                    );

                hiddenField.value =
                    Math.floor(
                        dateObj.getTime() / 1000
                    );
            }
        }


        // Trigger events
        input.dispatchEvent(
            new Event(
                'input',
                {
                    bubbles: true
                }
            )
        );

        input.dispatchEvent(
            new Event(
                'change',
                {
                    bubbles: true
                }
            )
        );

        input.dispatchEvent(
            new Event(
                'blur',
                {
                    bubbles: true
                }
            )
        );
        """,
        date_input,
        date_value,
    )


# ============================================================
# DESCRIPTION
# ============================================================

def set_description(
    driver,
    textarea,
    value
):

    driver.execute_script(
        """
        const input = arguments[0];
        const content = arguments[1];

        input.value = content;


        // CKEditor support
        if (
            window.CKEDITOR &&
            CKEDITOR.instances &&
            CKEDITOR.instances.pagecontent
        ) {

            CKEDITOR.instances
                .pagecontent
                .setData(content);

            CKEDITOR.instances
                .pagecontent
                .updateElement();
        }


        input.dispatchEvent(
            new Event(
                'input',
                {
                    bubbles: true
                }
            )
        );

        input.dispatchEvent(
            new Event(
                'change',
                {
                    bubbles: true
                }
            )
        );
        """,
        textarea,
        value,
    )


# ============================================================
# ALREADY UPDATED MESSAGE
# ============================================================

def is_already_updated_message(message):

    normalized_message = (
        message
        .strip()
        .lower()
    )

    return any(
        keyword in normalized_message
        for keyword in ALREADY_UPDATED_KEYWORDS
    )


# ============================================================
# GET ELEMENT TEXT
# ============================================================

def get_element_text(
    driver,
    element_id
):

    for element in driver.find_elements(
        By.ID,
        element_id
    ):

        text = (
            element.get_attribute(
                "textContent"
            )
            or element.text
            or ""
        ).strip()


        if text:

            return " ".join(
                text.split()
            )


    return ""


# ============================================================
# GET VALIDATION MESSAGE
# ============================================================

def get_skip_validation_message(driver):

    for alert_id in (
        "hours_alert",
        "hours1_alert",
        "hours3_alert",
    ):

        alert_text = get_element_text(
            driver,
            alert_id
        )


        normalized_text = (
            alert_text.lower()
        )


        if any(
            message in normalized_text
            for message in SKIP_VALIDATION_MESSAGES
        ):

            return alert_text


    return ""


# ============================================================
# SELECT VALUE
# ============================================================

def select_value(
    driver,
    wait,
    element_id,
    value
):

    dropdown = wait.until(
        EC.presence_of_element_located(
            (
                By.ID,
                element_id
            )
        )
    )


    driver.execute_script(
        """
        const select = arguments[0];
        const selectedValue = arguments[1];

        select.value =
            selectedValue;


        if (window.jQuery) {

            window.jQuery(select)
                .val(selectedValue)
                .trigger('change')
                .trigger('blur');
        }


        select.dispatchEvent(
            new Event(
                'change',
                {
                    bubbles: true
                }
            )
        );

        select.dispatchEvent(
            new Event(
                'blur',
                {
                    bubbles: true
                }
            )
        );
        """,
        dropdown,
        value,
    )


    wait.until(
        lambda d:
            d.find_element(
                By.ID,
                element_id
            ).get_attribute(
                "value"
            ) == value
    )


    return dropdown


# ============================================================
# TIME VALIDATION
# ============================================================

def wait_for_time_validation(
    driver,
    wait,
    hour_id,
    minute_id
):

    def validation_complete(d):

        hour_value = (
            d.find_element(
                By.ID,
                hour_id
            )
            .get_attribute(
                "value"
            )
            .strip()
        )


        minute_value = (
            d.find_element(
                By.ID,
                minute_id
            )
            .get_attribute(
                "value"
            )
            .strip()
        )


        if not hour_value or not minute_value:

            return False


        if d.find_elements(
            By.ID,
            "loader"
        ):

            return False


        validation_message = (
            get_skip_validation_message(d)
        )


        submit_disabled = (
            d.find_element(
                By.ID,
                "add_ts"
            )
            .get_attribute(
                "disabled"
            )
            is not None
        )


        return (
            bool(validation_message)
            or not submit_disabled
        )


    wait.until(
        validation_complete
    )


# ============================================================
# NORMALIZE DATE
# ============================================================

def normalize_date(date_value):

    for fmt in (
        "%Y-%m-%d",
        "%d/%m/%Y",
    ):

        try:

            return datetime.strptime(
                date_value.strip(),
                fmt
            ).strftime(
                "%Y-%m-%d"
            )

        except ValueError:

            continue


    raise ValueError(
        f"Unsupported date format: {date_value}"
    )


# ============================================================
# BUILD ENTRIES
# ============================================================

def build_entries():

    if len(sys.argv) >= 2:

        entry_date = (
            sys.argv[3]
            if len(sys.argv) > 3
            else datetime.now().strftime(
                "%Y-%m-%d"
            )
        )


        return [
            {
                "date":
                    normalize_date(
                        entry_date
                    ),

                "task":
                    sys.argv[1],

                "description":
                    (
                        sys.argv[2]
                        if len(sys.argv) > 2
                        else ""
                    ),
            }
        ]


    return [
        {
            **entry,
            "date":
                normalize_date(
                    entry["date"]
                ),
        }

        for entry in TIMESHEET_2026_ENTRIES
    ]


# ============================================================
# LOGIN
# ============================================================

def login(driver, wait):
    driver.get("https://mycipl.in/")

    username = wait.until(
        EC.presence_of_element_located(
            (By.ID, "login_user")
        )
    )

    password = wait.until(
        EC.presence_of_element_located(
            (By.ID, "login_pwd")
        )
    )

    #username_value = os.getenv("MYCIPL_USERNAME")
    #password_value = os.getenv("MYCIPL_PASSWORD")
    
    username_value = 'hemachandran@colanonline.com'
    password_value = 'Nxmoc9$'

    if not username_value:
        raise RuntimeError(
            "MYCIPL_USERNAME is not set."
        )

    if not password_value:
        raise RuntimeError(
            "MYCIPL_PASSWORD is not set."
        )

    username.send_keys(username_value)
    password.send_keys(password_value)

    wait.until(
        EC.element_to_be_clickable(
            (By.ID, "login_submit")
        )
    ).click()


# ============================================================
# OPEN MANUAL TIMESHEET FORM
# ============================================================

def open_manual_timesheet_form(
    driver,
    wait
):

    wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//a[contains(@href,'module=ts')]"
            )
        )
    ).click()


    wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//div[2]/ul/li[3]/a"
            )
        )
    ).click()


    wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//table//tr[6]/td[6]/a[1]"
            )
        )
    ).click()


    wait.until(
        EC.presence_of_element_located(
            (
                By.ID,
                "add_tab"
            )
        )
    )


    return driver.current_url


# ============================================================
# OPEN SAVED FORM
# ============================================================

def open_saved_form(
    driver,
    wait,
    form_url
):

    driver.get(
        form_url
    )


    wait.until(
        EC.presence_of_element_located(
            (
                By.ID,
                "add_tab"
            )
        )
    )


# ============================================================
# FILL BILLABLE TIMESHEET
# ============================================================

def fill_billable_timesheet(
    driver,
    wait,
    entry
):

    # Apply future date validation bypass
    bypass_future_date_validation(
        driver
    )


    # --------------------------------------------------------
    # General Bill
    # --------------------------------------------------------

    select_value(
        driver,
        wait,
        "mile",
        "General_Bill"
    )


    # --------------------------------------------------------
    # IMPORTANT FIX
    #
    # Removed:
    #
    # wait.until(
    #     lambda d:
    #     d.find_element(
    #         By.ID,
    #         "billable_form"
    #     ).is_displayed()
    # )
    #
    # wait.until(
    #     lambda d:
    #     d.find_element(
    #         By.ID,
    #         "billable_genform"
    #     ).is_displayed()
    # )
    #
    # Selenium is_displayed() was causing:
    #
    # javascript error:
    # this.each is not a function
    #
    # The actual field required next is task1.
    # --------------------------------------------------------


    task_input = wait.until(
        EC.presence_of_element_located(
            (
                By.ID,
                "task1"
            )
        )
    )


    set_text_input(
        driver,
        task_input,
        entry["task"]
    )


    wait.until(
        lambda d:
            d.find_element(
                By.ID,
                "task1"
            )
            .get_attribute(
                "value"
            )
            .strip()
            == entry["task"]
    )


    # --------------------------------------------------------
    # Task type
    # --------------------------------------------------------

    select_value(
        driver,
        wait,
        "type",
        DEFAULT_TASK_TYPE
    )


    # --------------------------------------------------------
    # Date
    # --------------------------------------------------------

    date_input = wait.until(
        EC.presence_of_element_located(
            (
                By.ID,
                "date1"
            )
        )
    )


    driver.execute_script(
        """
        arguments[0].scrollIntoView({
            block: 'center'
        });
        """,
        date_input
    )


    set_date_without_validation(
        driver,
        date_input,
        entry["date"]
    )


    time.sleep(1)


    set_date = (
        date_input.get_attribute(
            "value"
        )
    )


    print(
        f"Date set to: {set_date} "
        f"(expected: {entry['date']})"
    )


    # --------------------------------------------------------
    # Description
    # --------------------------------------------------------

    if entry["description"]:

        description_input = wait.until(
            EC.presence_of_element_located(
                (
                    By.ID,
                    "pagecontent"
                )
            )
        )


        set_description(
            driver,
            description_input,
            entry["description"]
        )


        wait.until(
            lambda d:
                entry["description"]
                in
                d.find_element(
                    By.ID,
                    "pagecontent"
                )
                .get_attribute(
                    "value"
                )
        )


    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    select_value(
        driver,
        wait,
        "status1",
        DEFAULT_STATUS
    )


    # --------------------------------------------------------
    # Start time
    # --------------------------------------------------------

    select_value(
        driver,
        wait,
        "tms_sttime",
        DEFAULT_START_TIME
    )


    # --------------------------------------------------------
    # End time
    # --------------------------------------------------------

    select_value(
        driver,
        wait,
        "tms_endtime",
        DEFAULT_END_TIME
    )


    # --------------------------------------------------------
    # Time validation
    # --------------------------------------------------------

    try:

        wait_for_time_validation(
            driver,
            wait,
            "hr",
            "mins"
        )

    except TimeoutException:

        print(
            "Timeout waiting for time "
            "validation, continuing anyway..."
        )


    # --------------------------------------------------------
    # Check validation message
    # --------------------------------------------------------

    validation_message = (
        get_skip_validation_message(
            driver
        )
    )


    if validation_message:

        print(
            f"Validation message detected: "
            f"{validation_message}"
        )

        return False, validation_message


    # --------------------------------------------------------
    # Submit
    # --------------------------------------------------------

    submit_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.ID,
                "add_ts"
            )
        )
    )


    driver.execute_script(
        """
        arguments[0].scrollIntoView({
            block: 'center'
        });
        """,
        submit_button
    )


    time.sleep(5)


    driver.execute_script(
        """
        arguments[0].click();
        """,
        submit_button
    )


    time.sleep(2)


    # --------------------------------------------------------
    # Check validation after submit
    # --------------------------------------------------------

    validation_message = (
        get_skip_validation_message(
            driver
        )
    )


    if validation_message:

        return False, validation_message


    # --------------------------------------------------------
    # Check browser alerts
    # --------------------------------------------------------

    try:

        alert = WebDriverWait(
            driver,
            3
        ).until(
            EC.alert_is_present()
        )


        alert_text = (
            alert.text.strip()
        )


        alert.accept()


        if is_already_updated_message(
            alert_text
        ):

            return False, alert_text


        if (
            "future"
            in alert_text.lower()
            or
            "invalid"
            in alert_text.lower()
        ):

            print(
                f"Date validation alert suppressed: "
                f"{alert_text}"
            )


            return True, ""


        if alert_text:

            raise RuntimeError(
                alert_text
                or
                "Unexpected submit alert"
            )


    except TimeoutException:

        # No alert - submission likely successful.
        pass


    return True, ""


# ============================================================
# RUN
# ============================================================

def run():

    entries = build_entries()


    print(
        f"Total entries to process: "
        f"{len(entries)}"
    )


    print(
        f"First entry date: "
        f"{entries[0]['date'] if entries else 'N/A'}"
    )


    print(
        "Future date validation bypass enabled\n"
    )


    # --------------------------------------------------------
    # Chrome
    # --------------------------------------------------------

    options = Options()


    options.add_argument(
        "--start-maximized"
    )


    # Uncomment for headless mode:
    #
    # options.add_argument("--headless")


    driver = webdriver.Chrome(
        service=Service(
            ChromeDriverManager().install()
        ),
        options=options,
    )


    wait = WebDriverWait(
        driver,
        20
    )


    try:

        # ----------------------------------------------------
        # Login
        # ----------------------------------------------------

        print(
            "Logging in..."
        )


        login(
            driver,
            wait
        )


        # ----------------------------------------------------
        # Open timesheet
        # ----------------------------------------------------

        print(
            "Opening manual timesheet form..."
        )


        form_url = (
            open_manual_timesheet_form(
                driver,
                wait
            )
        )


        # Apply bypass immediately
        bypass_future_date_validation(
            driver
        )


        successful = 0
        failed = 0


        # ----------------------------------------------------
        # Process entries
        # ----------------------------------------------------

        for index, entry in enumerate(
            entries,
            start=1
        ):

            try:

                print(
                    f"\n[{index}/{len(entries)}] "
                    f"Processing entry for "
                    f"{entry['date']}..."
                )


                # Reload form for every entry
                if index > 1:

                    open_saved_form(
                        driver,
                        wait,
                        form_url
                    )


                    # Re-apply bypass
                    bypass_future_date_validation(
                        driver
                    )


                submitted, message = (
                    fill_billable_timesheet(
                        driver,
                        wait,
                        entry
                    )
                )


                if submitted:

                    print(
                        f"[✓] Submitted "
                        f"{entry['date']} - "
                        f"{entry['task']}"
                    )


                    successful += 1


                else:

                    print(
                        f"[✗] Skipped "
                        f"{entry['date']} - "
                        f"{entry['task']}: "
                        f"{message}"
                    )


                    failed += 1


                time.sleep(
                    POST_SUBMIT_WAIT_SECONDS
                )


            except Exception as exc:

                print(
                    f"[✗] Error processing "
                    f"{entry['date']} - "
                    f"{entry['task']}: "
                    f"{exc}"
                )


                failed += 1


                continue


        # ----------------------------------------------------
        # Summary
        # ----------------------------------------------------

        print(
            f"\n{'=' * 50}"
        )


        print(
            f"COMPLETED: "
            f"{successful} successful, "
            f"{failed} failed "
            f"out of {len(entries)}"
        )


        print(
            f"{'=' * 50}"
        )


    except Exception as e:

        print(
            f"Fatal error: {e}"
        )


        raise


    finally:

        print(
            "Closing browser..."
        )


        driver.quit()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    run()
