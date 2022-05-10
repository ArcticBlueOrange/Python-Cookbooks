from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import SessionNotCreatedException
from webdriver_manager.chrome import ChromeDriverManager

import traceback
import time

__all__ = [
    'add_options',
#     'get_driver',
    
    'is_present',
    'get_selector',
    'select_and_click',
    'select_and_write',
]

"""
## Usage (on main script)
### First Steps
import selenium_cb as sel
driver_options = webdriver.ChromeOptions()
sel.add_options(driver_options)
driver = sel.get_driver('chrome')
driver.get(URL)
# Samples
### wait until an element is loaded
wait for download complete
donepath = "/html/body/nl-root/router-outlet/nl-alerts/div/div/div/p"
while not sel.is_present(driver, donepath, 'xpath'):
    time.sleep(1)
print(sel.get_selector(driver, donepath, 'xpath').text)

### input user and password
sel.select_and_write(driver, 'username', 'name', <USER>)
sel.select_and_write(driver, 'password', 'name', <PSWD>)
sel.select_and_click(driver, "signin_submit", 'id')

### ...and so on
Each select_and_do_stuff function have the same structure:
    - driver:        the browser or parent selector
    - selector_name: string; depends on the context
    - selector_type: 'css', 'xpath', etc.
    - [actions]:     misc
"""

DEBUG = False
DEFAULT_OPTIONS = [
    '--ignore-certificate-errors',
    '--ignore-ssl-errors',
    '--start-maximized',
    'log-level=3,
    '--silent',
    '--disable-gpu',
    '--headless',
    '--window-size=1920x1080',
]

## Functions to connect to driver
def _raise(ex):
    raise ex


def add_options(driver_options = DEFAULT_OPTIONS):
    for option in driver_options:
        driver_options.add_argument(option)

    
def get_driver(browser = 'chrome'):
    return {
        'chrome': lambda: webdriver.Chrome(ChromeDriverManager().install()),
    }.get( browser, lambda: _raise(TypeError(f'unsupported browser: {browser}')) )()


## Functions to easily interact w/ DOM
def try_with_errors(maxtries=10, waitseconds=1,
                    strict=True, verbose=DEBUG,
                    custom_error="Function failed after {} tries",
                    reraise = [KeyError] # Exceptions to not catch
                    ):
    def p(*args,**kwargs): # prints only if "verbose" is true
        if verbose:
            print(*args,**kwargs)
    def decorator(func):
        # The factory creates a custom decorator function
        def inner(*args,**kwargs):
            # The decorator is applied in the inner function
            counter = 0
            while counter < maxtries:
                p(f"Try number {counter+1}")
                try:
                    return func(*args,**kwargs)
                except Exception as e:
                    if type(e) in reraise:
                        raise
                    p(f"Exception: {traceback.format_exc()}")
                    counter += 1
                    time.sleep(waitseconds)
            if strict:
                raise RuntimeError(custom_error.format(maxtries))
            else:
                return None
        return inner
    return decorator


def generic_getter(driver, selector, selector_type='name'):
    return { 'id' : lambda d, s: d.find_element_by_id(s),
           'name' : lambda d, s: d.find_element_by_name(s),
          'xpath' : lambda d, s: d.find_element_by_xpath(s),
          'class' : lambda d, s: d.find_element_by_class_name(s),
            'css' : lambda d, s: d.find_element_by_css_selector(s),
    }[selector_type](driver, selector)


@try_with_errors(3, .1, False)
def is_present(driver, selector, sel_type='name'):
    "Return object or null - quick exit"
    return generic_getter(driver, selector, sel_type)


@try_with_errors(50, .1)
def get_selector(driver, selector, sel_type='name'):
    "Return object or fails"
    return generic_getter(driver, selector, sel_type)


@try_with_errors()
def select_and_click(d,s,sel_type):
    x = generic_getter(d,s,sel_type)
    x.click()
    return x


@try_with_errors()
def select_and_write(d,s,sel_type,message:str, overwrite=True):
    x = generic_getter(d,s,sel_type)
    if overwrite:
        x.clear()
    x.send_keys(message)
    return x

