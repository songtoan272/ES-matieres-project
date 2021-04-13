from elasticsearch import Elasticsearch, helpers, exceptions
from transform_data import *


class ES_Data:

    def __init__(self):
        self.es = Elasticsearch(
            [{'host': 'localhost', 'port': 9200}],
            timeout=100
        )
        if self.es.ping():
            print('Connected!')
        else:
            print('Connection Failed')

        try:
            self.es.search(index='subject')
            print("Subjects are already indexed.")
        except exceptions.NotFoundError as ex:
            # self.delete_index()
            self.create_index()
            self.index_json_file("./data/subjects.json")

    def create_index(self, index_name='subject', settings=None):
        created = False
        # index settings
        if not settings:
            settings = {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "analysis": {
                        "analyzer": {
                            "default": {
                                "type": "french"
                            }
                        },
                        "search_analyzer": {
                            "default": {
                                "type": "standard"
                            }
                        }
                    }
                },
                "mappings": {
                    "dynamic": "strict",
                    "properties": {
                        "name": {
                            "type": "text",
                            "fields": {
                                "raw": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "category": {
                            "type": "keyword"
                        },
                        "duration": {
                            "type": "integer"
                        },
                        "start_date": {
                            "type": "date",
                            "format": "dd-MM-yyyy || dd/MM/yyyy"
                        },
                        "end_date": {
                            "type": "date",
                            "format": "dd-MM-yyyy || dd/MM/yyyy"
                        },
                        "description": {
                            "type": "text",
                            "fields": {
                                "raw": {
                                    "type": "keyword",
                                    "ignore_above": 1000
                                }
                            }
                        },
                        "coefficient": {
                            "type": "byte"
                        },
                        "professor": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword"
                                        }
                                    }
                                },
                                "prof_name": {
                                    "properties": {
                                        "first": {"type": "text"},
                                        "last": {"type": "text"}
                                    }
                                }
                            }
                        },
                        "year": {
                            "type": "byte"
                        }
                    }

                }
            }
        try:
            if not self.es.indices.exists(index_name):
                # Ignore 400 means to ignore "Index Already Exist" error.
                self.es.indices.create(index=index_name, body=settings)
                print('Created Index')
            created = True
        except Exception as ex:
            print(str(ex))
        finally:
            return created

    def index_json_file(self, jsonFilePath, index_name='subject'):
        text_docs = get_data_from_text_file(jsonFilePath)
        doc_list = []
        for num, doc in enumerate(text_docs):
            dict_doc = json.loads(doc)
            dict_doc = preprocessing_subject(dict_doc, num)
            doc_list.append(dict_doc)
        resp = helpers.bulk(self.es, doc_list, index=index_name, doc_type='_doc')
        print("helpers.bulk() response: ", resp)

    def search(self, index_name='subject'):
        # es_query = {
        #
        #     'query': {
        #         "term": {
        #             "host.keyword": {
        #                 "value": "www.elastic.co"
        #             }
        #         }
        #     },
        #     'size': 10
        # }
        search_values = extract_search_input()

        print(search_values)
        # res = self.es.search(index=index_name, body=search)
        # print("Got %d Hits:" % res['hits']['total']['value'])
        # es_result = res['hits']['hits']
        #
        # result = "<br/>"
        # for c in es_result:
        #     result += str(c['_source']) + "<br/>"
        return search_values

    def delete_index(self, index_name='subject'):
        self.es.indices.delete(index=index_name, ignore=[400, 404])

    def delete_doc(self, id, index_name='subject'):
        self.es.delete(index=index_name, id=id)


if __name__ == "__main__":
    es = ES_Data()
    jsonFile = "./data/subjects.json"
    # es.index_json_file(jsonFile)
    es.search()
