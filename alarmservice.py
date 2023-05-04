from PyQt5.QtWidgets import QApplication
from flask import Flask, request, jsonify
from messagebox import AlarmMessageBox
import multiprocessing as mp
import sys

def _raise_msgbox(title, information):

    app = QApplication(sys.argv)
    box = AlarmMessageBox(titleFont="汉仪铸字木头人W", contentFont="汉仪铸字木头人W")
    
    box.set_infos(title, information)
    box.fadeup()
    sys.exit(app.exec_())

def raise_msgbox(title, information):
    '''raise a message box'''

    p = mp.Process(target=_raise_msgbox, args=(title, information))
    p.start()

app = Flask(__name__)

@app.route("/alarm", methods=["POST"])
def alarm():
    data = request.get_json()
    title = data.get("title")
    if title is None:
        title = "???"

    information = data.get("info")
    if information is None:
        information = "???"

    raise_msgbox(title, information)
    print(data)
    return jsonify({"code": 0, "message": "success"})



if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)