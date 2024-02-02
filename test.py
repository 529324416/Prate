
from flask import Flask
from prate import Prate

msgbox = Prate()

app = Flask(__name__)

@app.route("/ring")
def ring():
    msgbox.ring("Hello", "World")
    return "Ring"


if __name__ == "__main__":
    app.run()