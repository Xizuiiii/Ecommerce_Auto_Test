import os
from tempfile import TemporaryDirectory

import pytest


def test_saucedemo_login(pytestconfig):
    if not pytestconfig.getoption("--run-ui"):
        pytest.skip("UI test is optional. Run with --run-ui when Edge WebDriver is ready.")

    from selenium import webdriver
    from selenium.common.exceptions import WebDriverException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.edge.options import Options
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    edge_options = Options()
    edge_options.add_argument("--no-proxy-server")
    edge_options.add_argument("--ignore-certificate-errors")
    edge_options.add_argument("--disable-blink-features=AutomationControlled")
    edge_options.add_argument("--window-size=1440,900")

    if os.getenv("SHOP_UI_HEADLESS", "1").lower() not in {"0", "false", "no"}:
        edge_options.add_argument("--headless=new")

    with TemporaryDirectory(ignore_cleanup_errors=True) as user_data_dir:
        edge_options.add_argument(f"--user-data-dir={user_data_dir}")

        try:
            driver = webdriver.Edge(options=edge_options)
        except WebDriverException as exc:
            pytest.skip(f"Edge WebDriver is not available or could not start: {exc.msg}")

        try:
            wait = WebDriverWait(driver, 15)
            driver.get(os.getenv("SHOP_UI_BASE_URL", "https://www.saucedemo.com/"))

            wait.until(EC.visibility_of_element_located((By.ID, "user-name"))).send_keys(
                os.getenv("SHOP_UI_USERNAME", "standard_user")
            )
            driver.find_element(By.ID, "password").send_keys(
                os.getenv("SHOP_UI_PASSWORD", "secret_sauce")
            )
            driver.find_element(By.ID, "login-button").click()

            assert wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "title"))).text == "Products"
        finally:
            driver.quit()
