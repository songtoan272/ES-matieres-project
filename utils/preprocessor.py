import json

from flask import request

def split_prof_name(prof_name):
    prof_name_ = str.split(prof_name, " ", 2)
    dict_prof_name = {
        "title": prof_name_[0],
        "prof_name": {
            "first": prof_name_[2],
            "last": prof_name_[1]
        }
    }
    return dict_prof_name

def preprocessing_subject(dict_doc, num_id):
    dict_doc["_id"] = num_id
    dict_doc['professor'] = split_prof_name(dict_doc['professor'])
    dict_doc['coefficient'] = 0 if dict_doc['coefficient'] == 'N.C' else dict_doc['coefficient']
    return dict_doc

def extract_search_input():
    #TODO: validate input values
    input_criteria = ['keyword', 'cate_1', 'cate_2', 'cate_3',
                      'coef_1', 'coef_2', 'coef_3', 'coef_4',
                      'start_date_day', 'start_date_month', 'start_date_year',
                      'end_date_day', 'end_date_month', 'end_date_year', 'duration',
                      'year_3', 'year_4']
    inputs_dict = {criteria: request.form.get(criteria) for criteria in input_criteria}
    search_values = {}

    if inputs_dict['keyword']:
        search_values['keyword'] = inputs_dict['keyword']

    # if inputs_dict['category'] == 'iabd':
    #     search_values['category'] = 'A.I & Big Data'
    # elif inputs_dict['category'] == 'maths':
    #     search_values['category'] = 'Maths'
    # elif inputs_dict['category'] == 'dev':
    #     search_values['category'] = 'Développement & Programmation'

    search_values['category'] = []
    for cate in ['cate_1', 'cate_2', 'cate_3']:
        if inputs_dict[cate] == 'iabd':
            search_values['category'].append('A.I & Big Data')
        elif inputs_dict[cate] == 'maths':
            search_values['category'].append('Maths')
        elif inputs_dict[cate] == 'dev':
            search_values['category'].append('Développement & Programmation')
    if len(search_values['category']) == 0:
        search_values.pop('category')

    search_values['coef'] = []
    for coef in ['coef_1', 'coef_2', 'coef_3', 'coef_4']:
        coef_value = inputs_dict[coef]
        if coef_value and str.isdigit(coef_value):
            search_values['coef'].append(int(coef_value))
    if len(search_values['coef']) == 0:
        search_values.pop('coef')

    if (inputs_dict['start_date_day'] != "" and
            inputs_dict['start_date_month'] != "" and
            inputs_dict['start_date_year'] != ""):
        search_values['start_date'] = '{}-{}-{}'.format(
            inputs_dict['start_date_day'],
            inputs_dict['start_date_month'],
            inputs_dict['start_date_year'])

    if (inputs_dict['end_date_day'] != "" and
            inputs_dict['end_date_month'] != "" and
            inputs_dict['end_date_year'] != ""):
        search_values['end_date'] = '{}-{}-{}'.format(
            inputs_dict['end_date_day'],
            inputs_dict['end_date_month'],
            inputs_dict['end_date_year'])

    if inputs_dict['duration'] and str.isdigit(inputs_dict['duration']):
        search_values['duration'] = int(inputs_dict['duration'])

    search_values['year'] = []
    for year in ['year_3', 'year_4']:
        if search_values['year']:
            search_values['year'].append(int(inputs_dict[year]))
    if len(search_values['year']) == 0:
        search_values.pop('year')

    return search_values

def make_query():
    search_values = extract_search_input()
    es_query = {
        'query': {
            'bool': {
                # 'must': {},
                # 'must_not': {},
                # 'should': {},
                'filter': []
            }
        }
    }

    if 'keyword' in search_values:
        es_query['query']['bool']['filter'].append({'multi_match': {
            'query': search_values['keyword'],
            'fields': ['name', 'professor.prof_name.first',
                       'professor.prof_name.last', 'category', 'description']}
        })

    if 'category' in search_values:
        es_query['query']['bool']['filter'].append({'terms': {'category.keyword': search_values['category']}})

    if 'coef' in search_values:
        es_query['query']['bool']['filter'].append({'terms': {'coefficient': search_values['coef']}})

    if 'year' in search_values:
        es_query['query']['bool']['filter'].append({'terms': {'year': search_values['year']}})

    if 'start_date' in search_values:
        es_query['query']['bool']['filter'].append({'range': {'start_date': {'gte': search_values['start_date']}}})
    if 'end_date' in search_values:
        es_query['query']['bool']['filter'].append({'range': {'end_date': {'lte': search_values['end_date']}}})
    if 'duration' in search_values:
        es_query['query']['bool']['filter'].append({'range': {'duration': {'lte': search_values['duration']}}})

    print(json.dumps(es_query, indent=2))
    return es_query


