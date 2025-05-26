from threading import Thread

from flask import Flask

app = Flask("")


@app.route("/")
def index() -> str:
    return "Running"


def run() -> None:
    app.run(host="0.0.0.0", port=8080)


def keep_alive() -> None:
    t = Thread(target=run)
    t.start()
