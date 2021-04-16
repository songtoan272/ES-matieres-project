import json

from flask import request


def extract_search_input():
    input_criteria = ['keyword', 'cate_1', 'cate_2', 'cate_3', 'cate_4',
                      'coef_1', 'coef_2', 'coef_3', 'coef_4',
                      'start_date_day', 'start_date_month', 'start_date_year',
                      'end_date_day', 'end_date_month', 'end_date_year', 'duration',
                      'year_3', 'year_4', 'sort_field', 'sort_order']
    inputs_dict = {criteria: request.form.get(criteria) for criteria in input_criteria}
    search_values = {}

    if inputs_dict['keyword']:
        search_values['keyword'] = inputs_dict['keyword']

    search_values['category'] = []
    for cate in ['cate_1', 'cate_2', 'cate_3', 'cate_4']:
        if inputs_dict[cate] == 'iabd':
            search_values['category'].append('A.I & Big Data')
        elif inputs_dict[cate] == 'maths':
            search_values['category'].append('Maths')
        elif inputs_dict[cate] == 'dev':
            search_values['category'].append('Développement & Programmation')
        elif inputs_dict[cate] == 'general':
            search_values['category'].append('Général')
    if len(search_values['category']) == 0:
        search_values.pop('category')

    search_values['coef'] = []
    for coef in ['coef_1', 'coef_2', 'coef_3', 'coef_4']:
        coef_value = inputs_dict[coef]
        if coef_value and str.isdigit(coef_value):
            search_values['coef'].append(int(coef_value))
    if len(search_values['coef']) == 0:
        search_values.pop('coef')

    if (inputs_dict['start_date_day'] and
            inputs_dict['start_date_month'] and
            inputs_dict['start_date_year']):
        search_values['start_date'] = '{}-{}-{}'.format(
            inputs_dict['start_date_day'],
            inputs_dict['start_date_month'],
            inputs_dict['start_date_year'])

    if (inputs_dict['end_date_day'] and
            inputs_dict['end_date_month'] and
            inputs_dict['end_date_year']):
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

    search_values['sort'] = []
    if inputs_dict['sort_field'] == 'professor':
        search_values['sort'].append('professor.prof_name.first.keyword:{}'.format(inputs_dict['sort_order']))
        search_values['sort'].append('professor.prof_name.last.keyword:{}'.format(inputs_dict['sort_order']))
    else:
        search_values['sort'].append('{}:{}'.format(inputs_dict['sort_field'], inputs_dict['sort_order']))

    return search_values

def make_query():
    search_values = extract_search_input()
    es_query = {
        'query': {
            'bool': {
                'filter': []
            }
        }
    }

    if 'keyword' in search_values:
        es_query['query']['bool']['filter'].append({'multi_match': {
            'query': search_values['keyword'],
            'fields': ['name', 'professor.prof_name.fullname', 'category', 'description']}
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
    return es_query, search_values['sort']

def make_agg_query():
    bucket_field = request.form.get('bucket_field')
    metric_field = request.form.get('metric_field')
    metric_agg = request.form.get('metric_agg')

    agg_query = None

    if bucket_field:
        agg_query = {'aggs': {
            "bucket_agg": {}
        }}

        if bucket_field in ["professor.prof_name.fullname.keyword",
                            'category.keyword', 'year', 'coefficient']:
            agg_query['aggs']['bucket_agg']['terms'] = {'field': bucket_field}
        elif bucket_field == 'duration':
            agg_query['aggs']['bucket_agg']['range'] = {
                'field': bucket_field,
                'ranges': [
                    {'to': 10},
                    {'from': 10, 'to': 15},
                    {'from': 15, 'to': 20},
                    {'from': 20}
                ]
            }
        elif bucket_field in ['start_date', 'end_date']:
            agg_query['aggs']['bucket_agg']['date_histogram'] = {
                'field': bucket_field,
                'interval': 'month',
                'format': 'yyyy-mm'
            }
        print(agg_query)

        if metric_field:
            agg_query['aggs']['bucket_agg']['aggs'] = {}
            agg_query['aggs']['bucket_agg']['aggs']['metric_agg'] = {}
            if metric_field == 'doc':
                agg_query['aggs']['bucket_agg']['aggs']['metric_agg']['value_count'] = {'field': 'name.keyword'}
            elif metric_field in ['duration', 'start_date', 'end_date']:
                agg_query['aggs']['bucket_agg']['aggs']['metric_agg'][str.lower(metric_agg)] = {'field': metric_field}

    elif metric_field:
        agg_query = {'aggs': {
            "metric_agg": {}
        }}
        if metric_field == 'doc':
            agg_query['aggs']['metric_agg']['value_count'] = {'field': 'name.keyword'}
        elif metric_field in ['duration', 'start_date', 'end_date']:
            agg_query['aggs']['metric_agg'][str.lower(metric_agg)] = {'field': metric_field}
    print(agg_query)
    return agg_query
