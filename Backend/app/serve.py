import os

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        os.environ.get("APP_MODULE", "app.main:app"),
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8080")),
        workers=1,
        ws_max_size=65536,
    )
