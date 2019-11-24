from collections import deque
from pathlib import Path
from string import Template
from src import config
import asyncio

import aiohttp
from hjson import loads as hjson_loads

import logging
from pprint import pprint
from os import makedirs, path


class GitFetcher:
    allowed_files = {}
    root_folder = ""
    entity_name_key = ""
    query_get_folder_contents: Template = Template(Path("graphql/get_folder_contents.graphql").read_text())

    def __init__(self, commit_id: str = "master"):
        self.commit_id = commit_id
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def folders_to_string(init: list) -> str:
        return '/'.join(init)

    def querry_formatter(self, folder: list = "") -> dict:
        folder = f"{self.commit_id}:" + self.folders_to_string(folder)
        query = self.query_get_folder_contents.substitute(folder=folder, rep_user=config.REPOSITORY_USER,
                                                          rep_name=config.REPOSITORY_NAME)
        return {'query': query}

    async def fetch_data(self):
        self.logger.info(f'started fetching {self.root_folder}')
        fetched_data = await self.handle_request(deque_folders=deque([[self.root_folder]]))
        self.logger.info(f'ended fetching {self.root_folder}')
        return fetched_data

    async def handle_request(self, deque_folders):
        items = {}
        images = {}
        async with aiohttp.ClientSession() as http_client_session:
            while len(deque_folders) > 0:
                folder = deque_folders.popleft()
                while True:
                    response = await http_client_session.post(config.GIT_API_ENDPOINT,
                                                              json=self.querry_formatter(folder=folder),
                                                              headers=config.GIT_HEADERS)
                    try:
                        data = await response.json()
                    except Exception as E:
                        self.logger.error(f"""error in {folder}
                        error: {E}""")
                        continue
                    self.logger.debug(f"got data from {folder}")
                    if "data" not in data:
                        self.logger.warning(f"""Failed to fetch {folder},
                         reason: {data}""")
                        await asyncio.sleep(config.RETRY_GIT_REQUEST_TIME)
                        continue
                    else:
                        data = data["data"]["repository"]["folder"]["entries"]
                        break
                for item in data:
                    if item["type"] == "tree":
                        deque_folders.appendleft(folder + [item["name"]])
                    elif item["name"].endswith(".png"):
                        self.logger.debug(f"got image {item['name']}")
                        images[item[
                            "name"]] = f"https://raw.githubusercontent.com/{config.REPOSITORY_USER}/{config.REPOSITORY_NAME}/{self.commit_id}/{'/'.join(folder)}/{item['name']}"
                    elif item["name"].endswith(self.allowed_files):
                        item_data = hjson_loads(item["object"]["text"], strict=False)
                        items[item_data[self.entity_name_key] if self.entity_name_key else item["name"]] = item_data
        return {
            self.root_folder: {
                "data": items,
                'images': images
            }
        }
