from pathlib import Path
from pprint import pprint
from string import Template
import logging

import aiohttp
import asyncio

from src import config
from src.git import get_files_subclasses


class Controller:
    def __init__(self):
        self.query_get_last_release: Template = Template(Path("graphql/get_current_version.graphql").read_text())
        self.commit_id = ""
        self.release_link = ""
        self.current_version = ""
        self.latest_version = ""
        self.data_is_being_processed = False
        self.data = {}
        self.logger = logging.getLogger(__name__)

    async def execute(self):
        await self.get_versions()
        await self.update_data()

    def query_formatter(self) -> dict:
        query = self.query_get_last_release.substitute(rep_user=config.REPOSITORY_USER,
                                                       rep_name=config.REPOSITORY_NAME)
        return {'query': query}

    async def get_versions(self):
        try:
            with open('version.txt', 'r') as version_file:
                self.current_version = version_file.read()
        except OSError:
            pass

        async with aiohttp.ClientSession() as http_client_session:
            while True:
                response = await http_client_session.post(config.GIT_API_ENDPOINT,
                                                          json=self.query_formatter(),
                                                          headers=config.GIT_HEADERS)
                data = await response.json()
                if 'data' not in data:
                    self.logger.warning(f"Failed to fetch version info, waiting, {data}")
                    await asyncio.sleep(config.RETRY_GIT_REQUEST_TIME)
                    continue
                else:
                    data = data['data']['repository']['releases']['nodes'][0]
                    break
        self.release_link = data['url']
        self.commit_id = data['tag']['target']['oid']
        self.latest_version = data['tag']['name']
        self.logger.info(
            f"""
        Latest version is {self.latest_version}
        commit is {self.commit_id}""")

    async def update_data(self):
        if self.current_version != self.latest_version:
            self.data_is_being_processed = True
            self.logger.info("Started fetching all data")
            data = await get_files_subclasses.get_all_fetchers()
            self.logger.info("Finished fetching all data")
            pprint(data, depth=2)
