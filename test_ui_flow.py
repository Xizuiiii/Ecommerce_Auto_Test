import pytest


def test_saucedemo_login(pytestconfig):
    if not pytestconfig.getoption("--run-ui"):
        pytest.skip("UI test is optional. Run with --run-ui when Edge WebDriver is ready.")

    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.edge.options import Options

    edge_options = Options()
    edge_options.add_argument("--no-proxy-server")
    edge_options.add_argument("--ignore-certificate-errors")
    edge_options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Edge(options=edge_options)
    try:
        driver.get("https://www.saucedemo.com/")
        driver.find_element(By.ID, "user-name").send_keys("standard_user")
        driver.find_element(By.ID, "password").send_keys("secret_sauce")
        driver.find_element(By.ID, "login-button").click()

        assert driver.find_element(By.CLASS_NAME, "title").text == "Products"
    finally:
        driver.quit()
