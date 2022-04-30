# -*- coding: utf-8 -*-

##! export FLASK_APP=server.py ; python -m flask run
from flask import Flask, request, render_template, redirect, url_for
from markupsafe import escape
import caspertools
import json
import os
app = Flask(__name__, static_url_path='', static_folder='static')


@app.route('/', methods=['GET'])
def index():
    '''
    Главная страница сервиса
    '''
    return render_template('index.html', toptext="")


@app.route('/parse_input', methods=['GET', 'POST'])
def parse_input():
    '''
    AJAX-метод принимает входные данные пользователя и преобразует в json
    '''
    print(request.get_json())
    text = request.get_json()['text']
    result = caspertools.parse_raw(text)
    return json.dumps(result)


@app.route('/get_preprints', methods=['GET', 'POST'])
def get_preprints():
    '''
    AJAX-метод принимает входные данные пользователя, находит статьи и возвращает ссылки на них
    '''
    print(request.get_json())
    text = request.get_json()['text']
    items = caspertools.parse_raw(text)
    result = caspertools.collect_paper_meta(items)
    return json.dumps(result)


@app.route('/parse_and_save', methods=['GET', 'POST'])
def parse_and_save():
    '''
    AJAX-метод принимает метаданные о статьях, скачивает их и возвращает ссылку на архив с данными
    '''
    import string, random
    newid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
    jsn = request.get_json()
    items = jsn['items']
    keepPDF = jsn['keep-pdf']
    file = caspertools.download_and_parse_papers(items, "static/" + newid, keepPDF=keepPDF)
    return json.dumps({"url" : f"/{newid}/{file}", "id" : newid})