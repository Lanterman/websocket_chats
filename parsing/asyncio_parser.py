import os
import json
import random
import string
import httpx
import asyncio
import fake_useragent
import logging as log

from dotenv import load_dotenv
from bs4 import BeautifulSoup as BS


log.basicConfig(format="[%(asctime)s | %(levelname)s]: %(message)s", level=log.INFO, datefmt='%m.%d.%Y %H:%M:%S')
load_dotenv(dotenv_path="./parsing/.env")


class Settings:
    """Basic parser setup"""

    def __init__(self):
        self.base_url = os.environ.get("DOMAIN")
        self.login_url = os.environ.get("LOGIN_URL")
        self.register_url = os.environ.get("REGISTER_URL")
        self.login_information = {"username": "username", "password": "test_password"}
        self.register_information = {
            "password1": "test_password", "password2": "test_password",
            "first_name": "test", "last_name": "test", "email": "test_email@example.com"
        }



def info_log(func):
    """Decorator informing about the progress of the parser"""

    async def logs_output():
        log.info(msg="Started the asyncio parser")
        log.info(msg="Data is written to the data_by_asyncio_parser.json file")
        await func()
        log.info(msg="Finished the selenium parser")
        log.info(msg="Check the data_by_asyncio_parser.json file")

    return logs_output


def write_to_json_file(data: dict) -> None:
    """Write to json file"""

    with open(file="data_by_asyncio_parser.json", mode="w") as file:
        json.dump(obj=data, fp=file, indent=4, ensure_ascii=False)


def collect_dict(user_info: dict, chat_info_list: list) -> dict:
    """Collects all information in dictionary"""

    number_of_chats = len(chat_info_list)
    public_chats = sum(1 for index, _ in enumerate(chat_info_list) if chat_info_list[index]["is_password"] == "Нет")
    private_chats = number_of_chats - public_chats

    output_data = {
        "number_of_chats": number_of_chats,
        "number_of_public_chats": public_chats,
        "number_of_private_chats": private_chats,
        "user_info": user_info,
        "chat_without_user": chat_info_list
    }
    return output_data


def set_headers() -> dict:
    """Create fake user agent and add it to dict"""

    user = fake_useragent.UserAgent().random
    header = {'user-agent': user}
    return header


def create_random_username(length: int = 12) -> str:
    """Create random username for registration"""

    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def create_dict_with_user_info(html: BS) -> dict:
    """Create dict with user info from user profile"""

    user_info = {
        "username": html.find(name="i", attrs={"id": "username"}).text,
        "first_name": html.find(name="i", attrs={"id": "first_name"}).text,
        "last_name": html.find(name="i", attrs={"id": "last_name"}).text,
        "email": html.find(name="i", attrs={"id": "email"}).text,
        "is_superuser": html.find(name="i", attrs={"id": "is_superuser"}).text,
    }

    return user_info


def get_chat_users(data: str, chat_info: dict) -> dict:
    """Parses chat user"""

    html = BS(markup=data, features="html.parser")
    list_user_html = html.select("#list_users > p > .redirect")

    for user in list_user_html:
        user_info = {"username": user.text, "link": f"{settings.base_url}{user.attrs['href']}"}
        chat_info["chat_users"] = user_info

    return chat_info


async def authorization(html: BS, session: httpx.AsyncClient) -> BS:
    """Authentication and authorization user"""

    scrf = html.find(name="input", attrs={"name": "csrfmiddlewaretoken"}).get("value")
    settings.login_information["csrfmiddlewaretoken"] = scrf

    request = await session.post(url=settings.login_url, data=settings.login_information)
    html = BS(request.text, "html.parser")

    return html


async def registration(html: BS, session: httpx.AsyncClient) -> BS:
    """Registration user"""

    scrf = html.find(name="input", attrs={"name": "csrfmiddlewaretoken"}).get("value")

    settings.register_information["username"] = create_random_username()
    settings.register_information["csrfmiddlewaretoken"] = scrf

    request = await session.post(url=settings.register_url, data=settings.register_information)
    html = BS(request.text, "html.parser")

    return html


async def fetch(link:str, session: httpx.AsyncClient) -> httpx.Response:
    """Makes request"""

    request = await session.request(method="get", url=link)
    return request


async def get_user_info(html: BS, session: httpx.AsyncClient) -> dict:
    """Get user info"""

    link_to_user_profile = html.find(name="a", attrs={"class": "redirect"}).attrs["href"]
    request = await fetch(link_to_user_profile, session)
    html = BS(markup=request.text, features="html.parser")

    user_info = create_dict_with_user_info(html)

    return user_info


async def get_info_about_owner(session: httpx.AsyncClient, chat_owner_link: str) -> dict:
    """Makes request and parses info about chat owner"""

    response = await fetch(chat_owner_link, session)

    html = BS(markup=response.text, features="html.parser")

    return create_dict_with_user_info(html)


async def parse_chat_without_user(session: httpx.AsyncClient, chat_html) -> dict:
    """Parses chats without user from main page"""

    chat_name = chat_html.select(".chat_name > .redirect")[0]
    chat_owner_link = chat_html.select(".chat_owner_name > .redirect")[0].attrs["href"]
    is_password = chat_html.select(".is_password > i")[0].text

    chat_info = {
        "chat_name": {"name": chat_name.text, "link_to_chat": f"{settings.base_url}{chat_name.attrs['href']}"},
        "chat_owner": await get_info_about_owner(session, chat_owner_link),
        "chat_users": "",
        "is_password": is_password
    }

    return chat_info


async def chat_analysis(session: httpx.AsyncClient, chat_info: dict) -> dict:
    """Makes request and parses response data"""

    if chat_info["is_password"] == "Нет":
        link_to_chat = chat_info["chat_name"]["link_to_chat"]

        response = await fetch(link_to_chat, session)
        chat_info = get_chat_users(response.text, chat_info)

    return chat_info


async def create_task_list_for_parsing_chats(session: httpx.AsyncClient, html: BS) -> asyncio.Future:
    """Create task list for parsing chats without user from main page"""

    task_list = []
    chats_html = html.find_all(name="div", attrs={"class": "chat_without_me"})

    for chat_html in chats_html:
        task = asyncio.create_task(parse_chat_without_user(session, chat_html))
        task_list.append(task)

    return asyncio.gather(*task_list)


async def create_task_list_for_parsing_open_chats(session: httpx.AsyncClient, chats_info: list) -> asyncio.Future:
    """Create task lisk for parsing open chats"""

    task_list = []

    for chat_info in chats_info:
        task = asyncio.create_task(chat_analysis(session, chat_info))
        task_list.append(task)

    return asyncio.gather(*task_list)


@info_log
async def main() -> None:
    """Endpoint"""

    async with httpx.AsyncClient(base_url=settings.base_url, follow_redirects=True) as session:
        session.headers.update(set_headers())
        request = await session.get(url="/")
        html = BS(request.text, "html.parser")

        auth_html = await authorization(html, session)

        if auth_html.find(name="h1", attrs={"id": "title"}) is None:
            auth_html = await registration(html, session)

        user_info = await get_user_info(auth_html, session)

        chats_without_user = await create_task_list_for_parsing_chats(session, auth_html)

        task_list = await create_task_list_for_parsing_open_chats(session, await chats_without_user)

        output_data = collect_dict(user_info, await task_list)

        write_to_json_file(output_data)


if __name__ == "__main__":
    settings = Settings()
    asyncio.run(main())
