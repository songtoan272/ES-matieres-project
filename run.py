from flask import (Flask, request, make_response, render_template)
from ES_data import ES_Data
import requests

app = Flask(__name__, static_url_path='/static')


@app.route("/")
def hello():
    return "Running"


@app.route("/home")
def home():
    return render_template("content.html")


@app.route("/load")
def load():
    es = ES_Data()
    result_data = es.search()
    response = make_response(render_template("table.html", data=result_data))
    return response



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
