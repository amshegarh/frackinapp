import concurrent

import aiohttp
import asyncio
import git.get_files_subclasses

data = {}


async def data_routine():
    await asyncio.gather(
        # git.get_files_subclasses.RecipesFetcher().fetch_data(),
        # git.get_files_subclasses.MissionsFetcher().fetch_data(),
        # git.get_files_subclasses.QuestsFetcher().fetch_data(),
        # git.get_files_subclasses.CodexFetcher().fetch_data(),
        # git.get_files_subclasses.TenantsFetcher().fetch_data(),
        # git.get_files_subclasses.TechFetcher().fetch_data(),
        # git.get_files_subclasses.PlantsFetcher().fetch_data(),
        # git.get_files_subclasses.StatsFetcher().fetch_data(),
        # git.get_files_subclasses.StatsFetcher().fetch_data(),
        # git.get_files_subclasses.CollectionsFetcher().fetch_data(),
        # git.get_files_subclasses.BiomesFetcher().fetch_data(),
        git.get_files_subclasses.ObjectsFetcher().fetch_data()
    )
    return


# try:
#     asyncio.run(data_routine(), debug=True)
# except:
#     print("oof")
loop = asyncio.get_event_loop()
executor = concurrent.futures.ThreadPoolExecutor(15)
loop.set_default_executor(executor)
loop.run_until_complete(data_routine())
executor.shutdown(wait=True)
loop.close()
