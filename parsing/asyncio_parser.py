import os
import json
import random
import string
import asyncio
import fake_useragent
import logging as log

from requests.sessions import Session
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


def write_to_json_file(data: dict) -> None:
    """Write to json file"""

    with open(file="data_by_asyncio_parser.json", mode="w") as file:
        json.dump(obj=data, fp=file, indent=4, ensure_ascii=False)


def set_headers() -> dict:
    """Create fake user agent and add it to dict"""

    user = fake_useragent.UserAgent().random
    header = {'user-agent': user}
    return header


def create_random_username(length: int = 12) -> str:
    """Create random username for registration"""

    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def authorization(html: BS, session: Session) -> BS:
    """Authentication and authorization user"""

    scrf = html.find(name="input", attrs={"name": "csrfmiddlewaretoken"}).get("value")
    settings.login_information["csrfmiddlewaretoken"] = scrf

    request = session.post(url=settings.login_url, data=settings.login_information)
    html = BS(request.text, "html.parser")

    return html


def registration(html: BS, session: Session) -> BS:
    """Registration user"""

    scrf = html.find(name="input", attrs={"name": "csrfmiddlewaretoken"}).get("value")

    settings.register_information["username"] = create_random_username()
    settings.register_information["csrfmiddlewaretoken"] = scrf

    request = session.post(url=settings.register_url, data=settings.register_information)
    html = BS(request.text, "html.parser")

    return html


def get_user_info(html: BS, session: Session) -> dict:
    """Get user info"""

    link_to_user_profile = html.find(name="a", attrs={"class": "redirect"}).attrs["href"]

    request = session.get(url=f"{settings.base_url}{link_to_user_profile}")
    html = BS(markup=request.text, features="html.parser")

    user_info = {
        "username": html.find(name="i", attrs={"id": "username"}),
        "first_name": html.find(name="i", attrs={"id": "first_name"}),
        "last_name": html.find(name="i", attrs={"id": "last_name"}),
        "email": html.find(name="i", attrs={"id": "email"}),
        "is_superuser": html.find(name="i", attrs={"id": "is_superuser"}),
    }

    return user_info



async def create_task_list(html: BS, session: Session) -> tuple:
    """Create task lisk for concurrent execution of queries and analysis of their data"""




async def main() -> None:
    """Endpoint"""

    with Session() as session:
        session.headers = set_headers()
        request = session.get(settings.base_url)
        html = BS(request.text, "html.parser")

        auth_html = authorization(html, session)

        if auth_html.find(name="h1", attrs={"id": "title"}) is None:
            auth_html = registration(html, session)

        user_info = get_user_info(auth_html, session)  # write to json
        print(user_info)

        # output_data = await create_task_list(auth_html, session)

        # write_to_json_file(output_data)



if __name__ == "__main__":
    settings = Settings()
    asyncio.run(main())
