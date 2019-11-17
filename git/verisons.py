from pathlib import Path
from string import Template
import config


class Controller:
    def __init__(self, current_version: str = ""):
        self.query_get_last_release: Template = Template(Path("graphql/get_current_version.graphql").read_text())
        self.current_version = current_version

    def querry_formatter(self) -> dict:
        query = self.query_get_last_release.substitute(rep_user=config.REPOSITORY_USER,
                                                       rep_name=config.REPOSITORY_NAME)
        return {'query': query}
