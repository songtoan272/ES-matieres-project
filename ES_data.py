from elasticsearch import Elasticsearch, helpers


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

    def search(self, search, index_name='subject'):
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
        res = self.es.search(index=index_name, body=search, size=1000)
        print("Got %d Hits:" % res['hits']['total']['value'])
        es_result = res['hits']['hits']

        result = "<br/>"
        for c in es_result:
            result += str(c['_source']) + "<br/>"
        return result


    def create_index(self, index_name='subject'):
        created = False
        # index settings
        settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "subject": {
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
                        "coefficient": {
                            "type": "byte"
                        },
                        "professor": {
                            "type": "object",
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


    def delete_index(self, index_name='subjects'):
        self.es.indices.delete(index=index_name, ignore=[400, 404])