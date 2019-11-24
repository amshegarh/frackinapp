from os import getenv

REPOSITORY_USER = "sayterdarkwynd"
REPOSITORY_NAME = "FrackinUniverse"
GIT_API_ENDPOINT = 'https://api.github.com/graphql'
GIT_PA_TOKEN = getenv("GIT_PA_TOKEN")
GIT_HEADERS = {
    "Authorization": f"bearer {GIT_PA_TOKEN}"
}
RETRY_GIT_REQUEST_TIME = 15  # seconds
RETRY_GIT_VERSION_CHECK_TIME = 3600  # seconds
