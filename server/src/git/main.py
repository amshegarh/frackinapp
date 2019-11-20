import concurrent
import logging

import asyncio
import src.git.verisons

data = {}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def data_routine():
    version_controller = src.git.verisons.Controller()
    await version_controller.execute()
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
