import asyncio
import uvicorn
from fastapi import FastAPI
from routes import api_router, prefix
from repositories.db_transactions.sql_functions import create_all_tables
from utils.helper_functions import update_token


app = FastAPI(docs_url=prefix+"/docs", openapi_url=prefix+"/openapi.json")


async def initialize_and_start_server():
    await update_token()
    await create_all_tables()
    config = uvicorn.Config(app, host="0.0.0.0", port=8888)
    server = uvicorn.Server(config)
    await server.serve()

app.include_router(api_router)

if __name__ == "__main__":
    asyncio.run(initialize_and_start_server())
