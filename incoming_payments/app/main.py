import uvicorn
from fastapi import FastAPI
from routes import *


app = FastAPI(docs_url=prefix+"/docs", openapi_url=prefix+"/openapi.json")


async def initialize_and_start_server():
    await drop_all_tables(logger)
    await create_all_tables(logger)
    config = uvicorn.Config(app, host="0.0.0.0", port=8080)
    server = uvicorn.Server(config)
    await server.serve()


app.include_router(api_router)


if __name__ == "__main__":
    asyncio.run(initialize_and_start_server())
