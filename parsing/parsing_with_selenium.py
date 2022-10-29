import json

from selenium import webdriver
from selenium.webdriver.common import by


register_url = "http://127.0.0.1:8000/register/"
login_url = "http://127.0.0.1:8000/login/"
main_url = "http://127.0.0.1:8000/"


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


def get_chats_without_user(driver) -> list:
    """Get chats without user"""

    chats_info, links_to_owner = [], []
    chats = driver.find_elements(by.By.CLASS_NAME, "chat_without_me")

    for chat in chats:
        is_password = chat.find_element(by.By.CLASS_NAME, "is_password").find_element(by.By.TAG_NAME, "i").text
        chat_name = chat.find_element(by.By.CLASS_NAME, "chat_name").find_element(by.By.CLASS_NAME, "redirect")
        link = chat.find_element(by.By.CLASS_NAME, "chat_owner_name").find_element(
            by.By.CLASS_NAME, "redirect").get_attribute("href")

        chat_info = {
            "chat_name": {"name": chat_name.text, "link_to_chat": chat_name.get_attribute("href")},
            "chat_owner": "",
            "is_password": is_password
        }

        chats_info.append(chat_info)
        links_to_owner.append(link)

    add_owner = add_owner_to_chat(driver, links_to_owner, chats_info)

    return add_owner


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
    print("add register, info chat if it doesn't have password")
