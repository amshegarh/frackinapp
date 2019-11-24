from pathlib import Path
from string import Template
import logging
import pickle
import os

import aiohttp
import asyncio

from src import config
from src.git import get_files_subclasses


class Controller:
    def __init__(self):
        self.query_get_last_release: Template = Template(Path("graphql/get_current_version.graphql").read_text())
        self.current_version_info = {
            'version': "",
            'commit_id': "",
            'release_link': "",
        }
        self.latest_version_info = {
            'version': "",
            'commit_id': "",
            'release_link': "",
        }
        self.data_is_being_processed = False
        self.data = {}
        self.logger = logging.getLogger(__name__)
        self.load_local_files()

    async def execute(self):
        while True:
            await self.git_fetch_latest_version()
            await self.update_data()
            await asyncio.sleep(config.RETRY_GIT_VERSION_CHECK_TIME)

    def load_local_files(self):
        try:
            with open('version.pkl', 'rb') as file:
                self.current_version_info = pickle.load(file)
            with open('data.pkl', 'rb') as file:
                self.data = pickle.load(file)
        except OSError:
            self.logger.warning("Failed to load local version or data")

    def query_formatter(self) -> dict:
        query = self.query_get_last_release.substitute(rep_user=config.REPOSITORY_USER,
                                                       rep_name=config.REPOSITORY_NAME)
        return {'query': query}

    async def git_fetch_latest_version(self):
        async with aiohttp.ClientSession() as http_client_session:
            while True:
                response = await http_client_session.post(config.GIT_API_ENDPOINT,
                                                          json=self.query_formatter(),
                                                          headers=config.GIT_HEADERS)
                data = await response.json()
                if 'data' not in data:
                    self.logger.warning(f"""Failed to fetch version info
                     reason: {data}""")
                    await asyncio.sleep(config.RETRY_GIT_REQUEST_TIME)
                    continue
                else:
                    data = data['data']['repository']['releases']['nodes'][0]
                    break
        self.latest_version_info = {
            'version': data['tag']['name'],
            'commit_id': data['tag']['target']['oid'],
            'release_link': data['url'],
        }
        self.logger.info(
            f"""Latest version is {self.latest_version_info["version"]}
        commit is {self.latest_version_info["commit_id"]}""")

    async def update_data(self, forced=False):
        if self.current_version_info["version"] != self.latest_version_info["version"] \
                or len(self.data) == 0 \
                or forced:
            self.data_is_being_processed = True
            self.logger.info("Started fetching new data from git")
            data_raw = await get_files_subclasses.get_all_fetchers(commit_id=self.latest_version_info["version"])
            self.logger.info("Finished fetching new data from git")
            data = {}
            for item in data_raw:
                data.update(item)

            self.logger.info("Started processing data")
            for obj in data['objects']['data']:
                categories = []
                try:
                    categories = obj['interactData']['filter']
                except:
                    try:
                        categories = obj['upgradeStages'][-1]['interactData']['filter']
                    except:
                        pass
                if len(categories) != 0:
                    categories = set(categories)
                for recipe in data['recipes']['data']:
                    already_added = False
                    if len(categories) != 0:
                        # this is crafting station of some kind
                        recipe_categories = set(recipe['groups'])
                        if len(categories & recipe_categories) > 0:
                            if 'recipes' in obj:
                                obj['recipes'].append(recipe)
                            else:
                                obj['recipes'] = [recipe]
                            already_added = True

                    items = [item['item'] for item in recipe['input']] +\
                            [item['item'] for item in recipe['output']]
                    if obj in items and not already_added:
                        # found a recipe for object
                        if 'recipes' in obj:
                            obj['recipes'].append(recipe)
                        else:
                            obj['recipes'] = [recipe]

            for item in data['items']['data']:
                for recipe in data['recipes']['data']:
                    items = [item['item'] for item in recipe['input']] +\
                            [item['item'] for item in recipe['output']]
                    if item in items:
                        # found a recipe for object
                        if 'recipes' in item:
                            item['recipes'].append(recipe)
                        else:
                            item['recipes'] = [recipe]
            del data["recipes"]  # dont need recipes anymore, all are stored inside objects

            self.current_version_info = self.latest_version_info
            self.logger.info(f"""Finished preparing data
            Saving version {self.current_version_info["version"]}""")
            with open("data.pkl", "wb+", encoding="utf-8") as file:
                pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)
            with open("versions.pkl", "wb+", encoding="utf-8") as file:
                pickle.dump(self.current_version_info, file, protocol=pickle.HIGHEST_PROTOCOL)
            self.data = data
            self.data_is_being_processed = False

    def get_data(self):
        return {
            'data' : self.data,
            'outdated': self.data_is_being_processed,
            'no_data': len(self.data) == 0,
        }

    def clear_local_data(self):
        os.remove("versions.pkl")
        os.remove("data.pkl")
        self.update_data(forced=True)