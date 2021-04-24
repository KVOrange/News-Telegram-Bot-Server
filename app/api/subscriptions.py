from flask import Blueprint, request
from newsapi import NewsApiClient
from pydantic import BaseModel

import config
from app.handlers.json_handler import get_response
from app.models import User, Category, db, Keyword

module = Blueprint('subscriptions', __name__, url_prefix='/subscriptions')
news_api = NewsApiClient(api_key=config.api_token)


class AddCategory(BaseModel):
    category_name: str


class AddKeyword(BaseModel):
    keyword_name: str


@module.route('/categories/', methods=['GET', 'POST', 'DELETE'])
def categories():
    telegram_id = request.headers.get('Authorization')
    user = User.query.filter_by(telegram_id=telegram_id).first()
    if not user:
        return get_response(403, False, 'Пользователь не найден')
    user_cat = [cat.name for cat in user.categories]

    if request.method == 'GET':
        return get_response(200, True, '', categories=user_cat)

    if request.method == 'POST':
        try:
            req_data = AddCategory.parse_raw(request.data)
        except ValueError as error:
            return get_response(400, False, 'Проверьте правильность запроса', data=error.errors())
        if req_data.category_name in user_cat:
            return get_response(400, False, 'Подписка уже оформлена')
        all_categories = news_api.get_sources()['sources']
        new_cat = None
        for cat in all_categories:
            if cat['name'] == req_data.category_name:
                new_cat = {
                    'name': cat['name'],
                    'id': cat['id'],
                }
                break
        if not new_cat:
            return get_response(400, False, 'Подписка на данную категорию не найдена')
        cat_obj = Category(name=new_cat['name'], news_api_id=new_cat['id'], user_id=user.id)
        db.session.add(cat_obj)
        user.categories.append(cat_obj)
        db.session.commit()
        return get_response(200, True, '')

    if request.method == 'DELETE':
        category_name = request.args.get('category_name', default=None)
        user_cat = Category.query.filter_by(name=category_name, user_id=user.id).first()
        if not user_cat:
            return get_response(400, False, 'Категория не найдена')
        db.session.delete(user_cat)
        db.session.commit()
        return get_response(200, True, '')


@module.route('/categories/list')
def category_list():
    telegram_id = request.headers.get('Authorization')
    user = User.query.filter_by(telegram_id=telegram_id).first()
    if not user:
        return get_response(403, False, 'Пользователь не найден')
    user_cat = [cat.name for cat in user.categories]
    all_categories = news_api.get_sources()['sources']
    eng_cat = []
    for cat in all_categories:
        if cat['name'] in user_cat:
            continue
        if cat['language'] == 'en':
            eng_cat.append(cat)
    return get_response(200, True, '', categories=eng_cat)


@module.route('/keywords/', methods=['GET', 'POST', 'DELETE'])
def keywords():
    telegram_id = request.headers.get('Authorization')
    user = User.query.filter_by(telegram_id=telegram_id).first()
    if not user:
        return get_response(403, False, 'Пользователь не найден')
    user_keywords = [cat.name for cat in user.keywords]

    if request.method == 'GET':
        return get_response(200, True, '', keywords=user_keywords)

    if request.method == 'POST':
        try:
            req_data = AddKeyword.parse_raw(request.data)
        except ValueError as error:
            return get_response(400, False, 'Проверьте правильность запроса', data=error.errors())
        if req_data.keyword_name in user_keywords:
            get_response(400, False, 'Такое ключевое уже есть')
        new_keyword = Keyword(name=req_data.keyword_name, user_id=user.id)
        db.session.add(new_keyword)
        db.session.commit()
        return get_response(200, True, '', id=new_keyword.id)

    if request.method == 'DELETE':
        keyword_name = request.args.get('keyword_name', default=None)
        user_keyword = Keyword.query.filter_by(name=keyword_name, user_id=user.id).first()
        if not user_keyword:
            return get_response(400, False, 'Ключевое слово не найдено')
        db.session.delete(user_keyword)
        db.session.commit()
        return get_response(200, True, '')
