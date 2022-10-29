import json

from selenium import webdriver
from selenium.webdriver.common import by


login_url = "http://127.0.0.1:8000/login/"
main_url = "http://127.0.0.1:8000"


def write_to_json_file(data: dict) -> None:
    """Write to json file"""

    with open(file="websocket_chats.json", mode="w") as file:
        json.dump(obj=data, fp=file, indent=4, ensure_ascii=False)


def authorization(driver):
    """Authorization"""

    username = driver.find_element(by.By.NAME, "username")
    password = driver.find_element(by.By.NAME, "password")
    username.send_keys("lanterman")
    password.send_keys("karmavdele")
    driver.find_element(by.By.TAG_NAME, "form").submit()


def get_user_info(driver) -> dict:
    """Get user information"""

    auth_user = driver.find_element(by.By.CLASS_NAME, "redirect")
    user_info = {"username": auth_user.text, "link_to_user_profile": auth_user.get_attribute("href")}
    return user_info


def get_chats_without_user(driver) -> list:
    """Get chats without user"""

    chats_info = []
    chats = driver.find_elements(by.By.CLASS_NAME, "chat_without_me")

    for chat in chats:
        is_password = chat.find_element(by.By.CLASS_NAME, "is_password").find_element(by.By.TAG_NAME, "i").text
        chat_name = chat.find_element(by.By.CLASS_NAME, "chat_name").find_element(by.By.CLASS_NAME, "redirect")
        chat_owner = chat.find_element(by.By.CLASS_NAME, "chat_owner_name").find_element(by.By.CLASS_NAME, "redirect")

        chat_info = {
            "chat_name": {"name": chat_name.text, "link_to_chat": chat_name.get_attribute("href")},
            "chat_owner": {"name": chat_owner.text, "link_to_owner": chat_owner.get_attribute("href")},
            "is_password": is_password
        }

        chats_info.append(chat_info)

    return chats_info


def parsing_main_page(driver) -> dict:
    """Parsing main page"""

    main_page_info = {}

    user_info = get_user_info(driver)
    chats_without_user = get_chats_without_user(driver)

    main_page_info["user_info"] = user_info
    main_page_info["chats_without_user"] = chats_without_user

    return main_page_info


def main() -> None:
    """Main function"""

    driver = webdriver.Chrome()
    driver.get(url=login_url)

    authorization(driver)
    main_page_info = parsing_main_page(driver)

    write_to_json_file(main_page_info)


if __name__ == "__main__":
    main()
