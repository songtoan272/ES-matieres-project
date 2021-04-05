from flask import (Flask, request, make_response, render_template)
from elasticsearch import Elasticsearch, helpers
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


class ES_Data:

    def __init__(self):
        self.es = Elasticsearch(
            [
                'http://localhost:9200/'
            ],
            timeout=100
        )

    def search(self):
        es_query = {

            'query': {
                "term": {
                    "host.keyword": {
                        "value": "www.elastic.co"
                    }
                }
            },
            'size': 10
        }
        es_result = self.es.search(index="kibana_sample_data_logs", body=es_query, size=1000)['hits']['hits']

        result = "<br/>"
        for c in es_result:
            result += str(c['_source']) + "<br/>"
        return result

        return es_result


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
