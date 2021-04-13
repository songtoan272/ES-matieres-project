import csv, json, datetime
import pandas as pd
from flask import request


def make_json(csvFilePath, jsonFilePath):
    csv_file = pd.DataFrame(pd.read_csv(csvFilePath, sep=";", header=0, index_col=False))
    csv_file.to_json(jsonFilePath,
                     orient="records",
                     date_format="epoch",
                     force_ascii=False,
                     date_unit="s",
                     lines=True)

def get_data_from_text_file(jsonFile):
    return [l.strip() for l in open(jsonFile, 'r', encoding='utf-8', errors='ignore')]

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
    input_criteria = ['keyword', 'category', 'coef_1', 'coef_2', 'coef_3', 'coef_4',
                      'start_date_day', 'start_date_month', 'start_date_year',
                      'end_date_day', 'end_date_month', 'end_date_year', 'duration', 'year']
    inputs_dict = {criteria: request.form.get(criteria) for criteria in input_criteria}
    search_values = {}

    if inputs_dict['keyword']:
        search_values['keyword'] = inputs_dict['keyword']

    if inputs_dict['category'] == 'iabd':
        search_values['category'] = 'A.I & Big Data'
    elif inputs_dict['category'] == 'maths':
        search_values['category'] = 'Maths'
    elif inputs_dict['category'] == 'dev':
        search_values['category'] = 'Développement & Programmation'

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

    if inputs_dict['year'] and str.isdigit(inputs_dict['year']):
        search_values['year'] = int(inputs_dict['year'])

    return search_values


if __name__=="__main__":
    csvFile = "./data/subjects.csv"
    jsonFile = "./data/subjects.json"
    make_json(csvFile, jsonFile)