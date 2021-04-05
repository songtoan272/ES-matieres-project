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
        if self.es.ping():
            print('Connected!')
        else:
            print('Connection Failed')

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

    def create_index(self, index_name='ESproject'):
        created = False
        # index settings
        settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "subjects": {
                    "dynamic": "true",
                    "properties": {
                        "name": {
                            "type": "text"
                        },
                        "category": {
                            "type": "keyword"
                        },
                        "number_hours": {
                            "type": "integer"
                        },
                        "start_date": {
                            "type": "date",
                            "format": "dd-MM-yyyy"
                        },
                        "end_date": {
                            "type": "date",
                            "format": "dd-MM-yyyy"
                        },
                        "description": {
                            "type": "text",
                            "ignore_above": 500
                        },
                        "coef": {
                            "type": "byte"
                        },
                        "professor": {
                            "properties": {
                                "title": {
                                    "type": "text",
                                    "fields": {
                                        "type": "keyword"
                                    }
                                },
                                "name": {
                                    "first": {"type": "text"},
                                    "last": {"type": "text"}
                                }
                            }
                        }
                    }
                }
            }
        }
        try:
            if not self.es.indices.exists(index_name):
                # Ignore 400 means to ignore "Index Already Exist" error.
                self.es.indices.create(index=index_name, ignore=400, body=settings)
                print('Created Index')
            created = True
        except Exception as ex:
            print(str(ex))
        finally:
            return created


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
