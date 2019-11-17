from collections import deque
from json import dumps
from pathlib import Path
from string import Template
import config
import asyncio

import aiohttp
from hjson import loads as hjson_loads

from pprint import pprint
from os import makedirs, path


class GitFetcher:
    allowed_files = {}
    root_folder = ""
    entity_name_key = ""
    query_get_folder_contents: Template = Template(Path("graphql/get_folder_contents.graphql").read_text())

    def __init__(self, commit_id: str = "master"):
        self.commit_id = commit_id

    @staticmethod
    def folders_to_string(init: list) -> str:
        return '/'.join(init)

    def querry_formatter(self, folder: list = "") -> dict:
        folder = f"{self.commit_id}:" + self.folders_to_string(folder)
        query = self.query_get_folder_contents.substitute(folder=folder, rep_user=config.REPOSITORY_USER,
                                                          rep_name=config.REPOSITORY_NAME)
        return {'query': query}

    async def fetch_data(self):
        print(f'started {self.root_folder}')
        s = await self.handle_request(deque_folders=deque([[self.root_folder]]))

        makedirs(path.dirname(f"results/{self.root_folder}.txt"), exist_ok=True)
        with open(f"results/{self.root_folder}.txt", "w+", encoding='utf8') as file:
            pprint(s[self.root_folder], file, indent=4)
        with open(f"results/{self.root_folder}_images.txt", "w+", encoding='utf8') as file:
            pprint(s["images"], file, indent=4)
        print(f'ended {self.root_folder}')
        return s

    async def handle_request(self, deque_folders):
        items = {}
        images = {}
        result = {}
        async with aiohttp.ClientSession() as http_client_session:
            while len(deque_folders) > 0:
                folder = deque_folders.popleft()
                while True:
                    headers = {
                        "Authorization": f"bearer {config.GIT_PA_TOKEN}"
                    }

                    response = await http_client_session.post('https://api.github.com/graphql',
                                                              json=self.querry_formatter(folder=folder),
                                                              headers=headers)
                    data = await response.json()
                    print(f"got data {folder}")
                    if "data" not in data:
                        print(f"Failed to fetch {folder}, waiting 3s, data == {data}")
                        await asyncio.sleep(3)
                        continue
                    else:
                        data = data["data"]["repository"]["folder"]["entries"]
                        break
                for item in data:
                    if item["type"] == "tree":
                        deque_folders.appendleft(folder + [item["name"]])
                    elif item["name"].endswith(".png"):
                        images[item["name"]] = f"https://raw.githubusercontent.com/{config.REPOSITORY_USER}/{config.REPOSITORY_NAME}/{self.commit_id}/{'/'.join(folder)}/{item['name']}"
                    elif item["name"].endswith(self.allowed_files):
                        item_data = hjson_loads(item["object"]["text"], strict=False)
                        items[item_data[self.entity_name_key] if self.entity_name_key else item["name"]] = item_data
        result[self.root_folder] = items
        result["images"] = images
        return result
