"""Zero-dependency local server and static assets for representation review."""

from __future__ import annotations

import shutil
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from pathlib import Path


def copy_viewer_assets(output_dir: Path) -> None:
    assets = files("knowledge_compiler").joinpath("viewer_assets")
    for name in ("index.html", "viewer.css", "viewer.js"):
        output = output_dir / name
        with assets.joinpath(name).open("rb") as source, output.open("wb") as target:
            shutil.copyfileobj(source, target)


def create_viewer_server(directory: Path, host: str, port: int) -> ThreadingHTTPServer:
    if not (directory / "manifest.json").is_file():
        raise ValueError(f"viewer directory has no manifest.json: {directory}")
    handler = partial(SimpleHTTPRequestHandler, directory=str(directory))
    return ThreadingHTTPServer((host, port), handler)


def serve_viewer(directory: Path, host: str, port: int, *, open_browser: bool = False) -> None:
    server = create_viewer_server(directory, host, port)
    actual_port = server.server_address[1]
    url = f"http://{host}:{actual_port}/"
    print(f"Serving representation viewer at {url}", flush=True)
    print("Press Ctrl-C to stop.", flush=True)
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
