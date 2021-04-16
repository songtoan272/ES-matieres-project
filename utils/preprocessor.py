import json

from flask import request

def split_prof_name(prof_name):
    prof_name_ = str.split(prof_name, " ", 2)
    dict_prof_name = {
        "title": prof_name_[0],
        "prof_name": {
            "first": prof_name_[2],
            "last": prof_name_[1],
            "fullname": prof_name_[2] + " " + prof_name_[1]
        }
    }
    return dict_prof_name

def preprocessing_subject(dict_doc, num_id):
    dict_doc["_id"] = num_id
    dict_doc['professor'] = split_prof_name(dict_doc['professor'])
    dict_doc['coefficient'] = 0 if dict_doc['coefficient'] == 'N.C' else dict_doc['coefficient']
    return dict_doc

def translate_agg_result(response, sub_agg:bool):
    res = None
    if sub_agg:
        res = [{r['key']:
                    {
                        'doc_count': r['doc_count'],
                        'sub_agg': r['sub_agg']
                    }
        } for r in response.aggregations.main_agg]
    else:
        res = response.aggregations.main_agg
    return res
