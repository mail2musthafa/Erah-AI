"""FastAPI Server to host the Foundations Interactive Learning Studio."""

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI(title="Erah AI Foundations Interactive Studio")

UI_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount("/static", StaticFiles(directory=UI_DIR), name="static")


@app.get("/")
async def read_index():
    return FileResponse(os.path.join(UI_DIR, "index.html"))


@app.get("/style.css")
async def read_css():
    return FileResponse(os.path.join(UI_DIR, "style.css"))


@app.get("/app.js")
async def read_js():
    return FileResponse(os.path.join(UI_DIR, "app.js"))


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  🚀 ERAH AI FOUNDATIONS LAB RUNNING")
    print("  👉 Open in your browser: http://localhost:8080")
    print("=" * 65 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8080)
