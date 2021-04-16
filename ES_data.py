from elasticsearch import Elasticsearch, helpers, exceptions
from elasticsearch_dsl import Search, A
from utils.etl_search import *
from utils.IOHandler import *
from utils.preprocessor import *


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
                    "number_of_replicas": 0
                    # "analysis": {
                    #     "analyzer": {
                    #         "default": {
                    #             "type": "standard"
                    #         }
                    #     },
                    #     "search_analyzer": {
                    #         "default": {
                    #             "type": "standard"
                    #         }
                    #     }
                    # }
                },
                "mappings": {
                    "dynamic": "strict",
                    "properties": {
                        "name": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "category": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
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
                            "type": "text"
                        },
                        "coefficient": {
                            "type": "byte"
                        },
                        "professor": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "keyword"
                                },
                                "prof_name": {
                                    "properties": {
                                        "first": {
                                            "type": "text",
                                            "fields": {
                                                "keyword": {
                                                    "type": "keyword"
                                                }
                                            }
                                        },
                                        "last": {
                                            "type": "text",
                                            "fields": {
                                                "keyword": {
                                                    "type": "keyword"
                                                }
                                            }
                                        },
                                        "fullname": {
                                            "type": "text",
                                            "fields": {
                                                "keyword": {
                                                    "type": "keyword"
                                                }
                                            },
                                        },
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
        es_query, sort = make_query()
        search_result = self.es.search(index=index_name, body=es_query, size=1000, sort=sort)

        nb_hits = search_result['hits']['total']['value']
        es_result = search_result['hits']['hits']

        result = []
        for c in es_result:
            result.append(c['_source'])
        print(result)
        return (nb_hits, result)

    def aggregation(self, index_name='subject'):
        agg_query = make_agg_query()
        if agg_query:
            res = self.es.search(index=index_name, body=agg_query, size=1000)
            print(json.dumps(res))
            return res
        else:
            return None

    def aggregation_dsl(self, index_name='subject'):
        bucket_field = request.form.get('bucket_field')
        metric_field = request.form.get('metric_field')
        metric_agg = request.form.get('metric_agg')

        if bucket_field:
            s = Search(using=self.es, index=index_name)
            if bucket_field in ["professor.prof_name.fullname.keyword",
                                'category.keyword', 'year', 'coefficient']:
                s.aggs.bucket('main_agg', 'terms', field=bucket_field)
            elif bucket_field == 'duration':
                s.aggs.bucket('main_agg', 'ranges', field=bucket_field,
                              ranges=[
                                  {'to': 10},
                                  {'from': 10, 'to': 15},
                                  {'from': 15, 'to': 20},
                                  {'from': 20}
                              ])

            elif bucket_field in ['start_date', 'end_date']:
                s.aggs.bucket('main_agg', 'date_histogram', field=bucket_field,
                              interval='month', format='yyyy-mm')
            if metric_field:
                if metric_field == 'doc':
                    s.aggs['main_agg'].metric('sub_agg', 'value_count',
                                                field='name.keyword')
                elif metric_field in ['duration', 'start_date', 'end_date']:
                    s.aggs['main_agg'].metric('sub_agg', str.lower(metric_agg),
                                                field=metric_field)
            res = s.execute()
            return s.to_dict(), translate_agg_result(res, True)

        elif metric_field:
            s = Search(using=self.es, index=index_name)
            if metric_field == 'doc':
                s.aggs.metric('main_agg', 'value_count', field='name.keyword')
            elif metric_field in ['duration', 'start_date', 'end_date']:
                s.aggs.metric('main_agg', str.lower(metric_agg), field=metric_field)
            res = s.execute()
            return s.to_dict(), translate_agg_result(res, False)
        return None, None

    def delete_index(self, index_name='subject'):
        self.es.indices.delete(index=index_name, ignore=[400, 404])

    def delete_doc(self, id, index_name='subject'):
        self.es.delete(index=index_name, id=id)


if __name__ == "__main__":
    es = ES_Data()
    jsonFile = "./data/subjects.json"
    # es.index_json_file(jsonFile)
    es.search()
