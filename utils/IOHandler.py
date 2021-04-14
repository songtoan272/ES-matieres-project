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

if __name__=="__main__":
    csvFile = "./data/subjects.csv"
    jsonFile = "./data/subjects.json"
    make_json(csvFile, jsonFile)