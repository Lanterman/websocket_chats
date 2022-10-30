from selenium import webdriver
from selenium.webdriver.common import by
from channels.testing import ChannelsLiveServerTestCase


class Config(ChannelsLiveServerTestCase):
    """Config class"""

    fixtures = ["test/mydata.json"]

    @classmethod
    def setUpClass(cls):
        option = webdriver.ChromeOptions()
        option.add_argument("headless")
        cls.driver = webdriver.Chrome(options=option)

    @classmethod
    def tearDownClass(cls):
        cls.driver.close()

    def authentication(self, username="username"):
        """Authentication for tests"""

        self.driver.get(f"{self.live_server_url}/login/")
        self.driver.find_element(by.By.NAME, "username").send_keys(username)
        self.driver.find_element(by.By.NAME, "password").send_keys("test_password")
        self.driver.find_element(by.By.TAG_NAME, "form").submit()


class TestUser(Config):
    """Testing user registration and authentication"""

    def test_1_valid_register(self):
        """Testing valid registration"""

        self.driver.get(f"{self.live_server_url}/register/")
        self.driver.find_element(by.By.NAME, "username").send_keys("test")
        self.driver.find_element(by.By.NAME, "password1").send_keys("test_password")
        self.driver.find_element(by.By.NAME, "password2").send_keys("test_password")
        self.driver.find_element(by.By.NAME, "first_name").send_keys("test")
        self.driver.find_element(by.By.NAME, "last_name").send_keys("test")
        self.driver.find_element(by.By.NAME, "email").send_keys("test@example.com")
        self.driver.find_element(by.By.TAG_NAME, "form").submit()
        assert self.driver.current_url[22:] == "/", self.driver.current_url[22:]

    def test_1_invalid_register(self):
        """Testing invalid registration"""

        self.driver.get(f"{self.live_server_url}/register/")
        self.driver.find_element(by.By.NAME, "username").send_keys("username")
        self.driver.find_element(by.By.NAME, "password1").send_keys("test_password")
        self.driver.find_element(by.By.NAME, "password2").send_keys("test_password")
        self.driver.find_element(by.By.NAME, "first_name").send_keys("test")
        self.driver.find_element(by.By.NAME, "last_name").send_keys("test")
        self.driver.find_element(by.By.NAME, "email").send_keys("test@example.com")
        self.driver.find_element(by.By.TAG_NAME, "form").submit()
        assert self.driver.current_url[22:] == "/register/", self.driver.current_url[22:]

    def test_2_valid_login(self):
        """Testing valid authentication"""

        self.authentication()
        assert self.driver.current_url[22:] == "/", self.driver.current_url[22:]

    def test_2_invalid_login(self):
        """Testing invalid authentication"""

        self.authentication(username="test")
        assert self.driver.current_url[22:] == "/login/", self.driver.current_url[22:]


class TestChat(Config):
    """Testing adding and viewing chat"""

    def test_1_chat_without_me(self):
        """Testing tag with ID chats_without_me"""

        self.authentication()
        self.driver.get(self.live_server_url)
        chat = self.driver.find_element(by.By.CLASS_NAME, "chat_name").find_element(by.By.CLASS_NAME, "redirect")
        assert self.driver.current_url[22:] == "/", self.driver.current_url[22:]
        assert chat.text == "lan1", chat.text
        assert chat.get_attribute("href")[22:] == "/chat/1/", chat.get_attribute("href")[22:]

    def test_2_delete_chat(self):
        """Testing delete chat"""
        self.authentication()
        self.driver.get(f"{self.live_server_url}/chat/1/")
        title = self.driver.find_element(by.By.ID, "title_chat")
        assert self.driver.current_url[22:] == "/chat/1/", self.driver.current_url[22:]
        assert title.text == 'Добро пожаловать в чат "lan1"', title.text

        self.driver.get(f"{self.live_server_url}/chat/1/delete/")
        assert self.driver.current_url[22:] == "/", self.driver.current_url[22:]
