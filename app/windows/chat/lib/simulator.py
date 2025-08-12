from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from seleniumbase import Driver


class AI:
    def __init__(self):
        self.driver = None
        self.responses = []
        self.use = 'chatgpt'

    def reload(self, use):
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print('Error quitting driver:', e)
                pass

        self.driver = Driver(uc=True, headless=False, disable_csp=True)
        self.use = use

        if self.use == 'chatgpt':
            self.driver.uc_open('https://chat.openai.com/')

            if self.driver.is_element_visible('[data-testid="close-button"]'):
                self.driver.find_element(By.CSS_SELECTOR, '[data-testid="close-button"]').click()

        elif self.use == 'grok':
            self.driver.uc_open('https://grok.com')
        self.responses = []
        print('AI loaded')

    def refresh(self):
        try:
            if self.driver:
                self.driver.refresh()
                self.responses = []
        except Exception as e:
            print('Error refreshing, reloading:', e)
            self.reload(self.use)

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print('Error quitting driver:', e)
            self.driver = None

    def submit(self, msg, img_path=None):
        if self.use == 'chatgpt':
            return self.gpt(msg, img_path)
        elif self.use == 'grok':
            return self.grok(msg, img_path)

    def gpt(self, msg, img_path=None):

        text_input = self.driver.find_element(By.CLASS_NAME, 'ProseMirror')
        text_input.send_keys(msg)

        if img_path:
            file_input = self.driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
            file_input.send_keys(img_path)

        wait = WebDriverWait(self.driver, 30)
        button = wait.until(expected_conditions.element_to_be_clickable((By.ID, "composer-submit-button")))
        button.click()

        print('Waiting for ".markdown" tag...')
        wait.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'markdown')))

        while True:
            try:
                yield self.driver.find_elements(By.CLASS_NAME, 'markdown')[-1].get_attribute('outerHTML')
            except StaleElementReferenceException:
                print('StaleElementReferenceException, retrying...')
                continue
            except NoSuchElementException:
                print('NoSuchElementException, retrying...')
                continue
            except Exception as e:
                print('Unexpected error:', e)
                continue

            try:
                self.driver.find_element(By.CSS_SELECTOR, '[aria-label="Stop streaming"]')
            except NoSuchElementException:
                break

        self.responses.append(self.driver.find_elements(By.CLASS_NAME, 'markdown')[-1].get_attribute('outerHTML'))
        yield self.responses[-1]

    def grok(self, msg, img_path=None):
        return ''
