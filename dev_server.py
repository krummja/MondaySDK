from __future__ import annotations
from typing import Callable
import os
import re
import shutil
from threading import Timer
from fastapi import FastAPI


def open_tunnel(port: int, subdomain: str | None = None) -> int:
    if not shutil.which('lt'):
        print("Getting localtunnel from Node...")
        os.system('npm install -g localtunnel')

    print(f"Attempting to open local tunnel on port {port}...")
    command = f'lt -p {port}'

    if subdomain:
        subdomain = subdomain.strip()
        subdomain = subdomain.replace('.', '-')
        subdomain = subdomain.replace(' ', '-')
        if re.match(r"^[\w-]+$", subdomain):
            command += f' -s {subdomain.lower()}'

        print(f"Using subdomain '{subdomain}'.")

    output = os.system(command)
    return output


def start_localtunnel(port: int, subdomain: str | None = None) -> None:
    address = open_tunnel(port, subdomain)
    print(address)


def with_localtunnel(
    app: FastAPI,
    run: Callable[..., None],
    subdomain: str | None = None
) -> Callable[..., None]:

    def tunnelled_run(*args, **kwargs) -> None:
        _port = kwargs.get('port', 8080)
        _thread = Timer(1, start_localtunnel, args=(_port, subdomain))
        _thread.daemon = True
        _thread.start()

        run(app, *args, **kwargs)

    return tunnelled_run
