from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException, WebDriverException
from selenium.webdriver.firefox.options import Options
import time


def clean_html(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find and remove all <script> tags
        for script in soup.find_all("script"):
            script.decompose()

        # Find and remove all <style> tags
        for style in soup.find_all("style"):
            style.decompose()

        # Return the modified HTML
        clean_html = str(soup)
        return clean_html
    except Exception as e:
        raise ValueError(f"Error processing HTML content: {e}")


def load_form_source(form_url, headless=True, implicit_wait=30, load_timeout=30, sleep_time=10):
    """
    Loads a form URL using Selenium and returns the rendered HTML.

    :param form_url: The URL of the form to load.
    :param headless: Run Firefox in headless mode if True, otherwise in normal mode.
    :param implicit_wait: Time in seconds the driver waits for elements to become available.
    :param load_timeout: Time in seconds before a page load timeout occurs.
    :param sleep_time: Time in seconds to wait for the page to fully render.
    :return: Rendered HTML of the page.
    """
    options = Options()
    if headless:
        options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    try:
        driver.implicitly_wait(implicit_wait)
        driver.set_page_load_timeout(load_timeout)
        driver.get(form_url)
        time.sleep(sleep_time)  # Wait for the page to load completely
        rendered_html = clean_html(driver.page_source)
        current_url = driver.current_url
        return rendered_html, current_url
    except TimeoutException:
        raise TimeoutException("Page load timed out.")
    except WebDriverException as e:
        raise WebDriverException(f"WebDriver encountered an error: {e}")
    finally:
        driver.quit()
