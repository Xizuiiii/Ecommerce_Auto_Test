# Ecommerce_Auto_Test

## Ecommerce API E2E Tests

This project runs live API tests against DummyJSON by default and can optionally run a Selenium UI smoke test against Sauce Demo.

## Install

```powershell
python -m pip install -r requirements.txt
```

If `python` is not on PATH in Codex Desktop, use the bundled runtime:

```powershell
C:\Users\Zebra\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pip install -r requirements.txt
```

## Run API tests

```powershell
python -m pytest -q
```

If the project virtual environment is unavailable, use the bundled Codex runtime:

```powershell
C:\Users\Zebra\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q
```

The default credentials are DummyJSON public test credentials:

```powershell
$env:SHOP_API_BASE_URL = "https://dummyjson.com"
$env:SHOP_API_USERNAME = "emilys"
$env:SHOP_API_PASSWORD = "emilyspass"
```

## Run UI smoke test

```powershell
python -m pytest -q --run-ui
```

The UI test runs Edge in headless mode by default and requires Microsoft Edge plus a compatible WebDriver setup. To see the browser window:

```powershell
$env:SHOP_UI_HEADLESS = "0"
python -m pytest -q --run-ui
```
