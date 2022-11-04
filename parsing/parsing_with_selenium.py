import os
import json
import logging as log

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common import by


log.basicConfig(format="[%(asctime)s | %(levelname)s]: %(message)s", level=log.INFO, datefmt='%m.%d.%Y %H:%M:%S')
load_dotenv(dotenv_path="./parsing/.env")


def write_to_json_file(data: dict) -> None:
    """Write to json file"""

    with open(file="parsing_with_selenium.json", mode="w") as file:
        json.dump(obj=data, fp=file, indent=4, ensure_ascii=False)


def registration(driver) -> None:
    """Registration"""

    driver.find_element(by.By.NAME, "username").send_keys("username")
    driver.find_element(by.By.NAME, "password1").send_keys("test_password")
    driver.find_element(by.By.NAME, "password2").send_keys("test_password")
    driver.find_element(by.By.NAME, "first_name").send_keys("test")
    driver.find_element(by.By.NAME, "last_name").send_keys("test")
    driver.find_element(by.By.NAME, "email").send_keys("test@example.com")
    driver.find_element(by.By.TAG_NAME, "form").submit()


def authorization(driver) -> None:
    """Authorization"""

    driver.find_element(by.By.NAME, "username").send_keys("username")
    driver.find_element(by.By.NAME, "password").send_keys("test_password")
    driver.find_element(by.By.TAG_NAME, "form").submit()


def get_user_info(driver) -> dict:
    """Get user information"""

    auth_user = driver.find_element(by.By.CLASS_NAME, "redirect")
    user_info = {"username": auth_user.text, "link_to_user_profile": auth_user.get_attribute("href")}
    return user_info


def add_owner_to_chat(driver, link_list: list, chats_info: list) -> list:
    """Add owner info to chats"""

    for number, link in enumerate(link_list):
        driver.get(link)
        owner = driver.find_element(by.By.ID, "user_info")

        owner_info = {
            "username": owner.find_element(by.By.ID, "username").text,
            "first_name": owner.find_element(by.By.ID, "first_name").text,
            "last_name": owner.find_element(by.By.ID, "last_name").text,
            "email": owner.find_element(by.By.ID, "email").text,
            "is_admin": owner.find_element(by.By.ID, "is_superuser").text,
        }

        chats_info[number]["chat_owner"] = owner_info

    return chats_info


def get_users_in_chat(driver, links_to_chat: list, chats_info: list) -> list:
    """Add users who are in chat if there is no password in chat"""

    for link in links_to_chat:
        driver.get(link)
        user_list = driver.find_element(by.By.ID, "list_users").find_elements(by.By.CLASS_NAME, "redirect")

        for elem in chats_info:
            if not elem["chat_users"] and elem["is_password"] != "Да":
                elem["chat_users"] = [{"username": user.text, "link": user.get_attribute("href")} for user in user_list]

        driver.get(url=f"{os.getenv('DOMAIN')}/chat/{link[27:-1]}/leave/")

    return chats_info


def get_chats_without_user(driver) -> list:
    """Get chats without user"""

    chats_info, links_to_owner, links_to_chat = [], [], []
    chats = driver.find_elements(by.By.CLASS_NAME, "chat_without_me")

    for chat in chats:
        chat_name = chat.find_element(by.By.CLASS_NAME, "chat_name").find_element(by.By.CLASS_NAME, "redirect")
        link_to_owner = chat.find_element(by.By.CLASS_NAME, "chat_owner_name").find_element(
            by.By.CLASS_NAME, "redirect").get_attribute("href")
        is_password = chat.find_element(by.By.CLASS_NAME, "is_password").find_element(by.By.TAG_NAME, "i").text

        chat_info = {
            "chat_name": {"name": chat_name.text, "link_to_chat": chat_name.get_attribute("href")},
            "chat_owner": "",
            "chat_users": "",
            "is_password": is_password
        }

        chats_info.append(chat_info)
        links_to_owner.append(link_to_owner)

        if is_password != "Да":
            links_to_chat.append(chat_name.get_attribute("href"))

    add_owner = add_owner_to_chat(driver, links_to_owner, chats_info)
    users_in_chat = get_users_in_chat(driver, links_to_chat, add_owner)

    return users_in_chat


def parsing_main_page(driver) -> None:
    """Parsing main page"""

    user_info = get_user_info(driver)
    chats_without_user = get_chats_without_user(driver)

    data = {"user_info": user_info, "chats_without_user": chats_without_user}

    write_to_json_file(data)


def info_log(func):
    """Decorator informing about the progress of the parser"""

    def logs_output():
        log.info(msg="Started the selenium parser")
        log.info(msg="Data is written to the parsing_with_selenium.json file")
        func()
        log.info(msg="Finished the selenium parser")
        log.info(msg="Check the parsing_with_selenium.json file")

    return logs_output


def set_option():
    """Set options for webdriver"""

    option = webdriver.ChromeOptions()
    option.add_argument("headless")
    return option


@info_log
def main() -> None:
    """Main function"""

    option = set_option()
    driver = webdriver.Chrome(options=option)
    driver.get(url=os.getenv('LOGIN_URL'))

    authorization(driver)

    if driver.current_url == os.getenv('LOGIN_URL'):
        driver.get(url=os.getenv('REGISTER_URL'))
        registration(driver)

    parsing_main_page(driver)


if __name__ == "__main__":
    main()
