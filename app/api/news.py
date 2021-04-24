from flask import Blueprint, request
from newsapi import NewsApiClient

import config
from app.handlers.json_handler import get_response
from app.models import User

module = Blueprint('news', __name__, url_prefix='/news')
news_api = NewsApiClient(api_key=config.api_token)


@module.route('/categories/')
def categories_news():
    telegram_id = request.headers.get('Authorization')
    user = User.query.filter_by(telegram_id=telegram_id).first()
    if not user:
        return get_response(403, False, 'Пользователь не найден')
    user_cats_id = ''
    for cat in user.categories:
        user_cats_id += cat.news_api_id + ','
    if not user_cats_id:
        return get_response(400, False, 'Вы ещё не подписались ни на один канал!')
    user_cats_id = user_cats_id[:-1]
    news_list = news_api.get_top_headlines(sources=user_cats_id)['articles'][:10]
    return get_response(200, True, '', news_list=news_list)


@module.route('/keywords/')
def keywords_news():
    telegram_id = request.headers.get('Authorization')
    user = User.query.filter_by(telegram_id=telegram_id).first()
    if not user:
        return get_response(403, False, 'Пользователь не найден')
    user_keywords_names = ''
    for keyword in user.keywords:
        user_keywords_names += keyword.name + ' OR '
    if not user_keywords_names:
        return get_response(400, False, 'У вас ещё нет ключевых слов!')
    user_keywords_names = user_keywords_names[:-4]
    news_list = news_api.get_top_headlines(q=user_keywords_names)['articles'][:10]
    return get_response(200, True, '', news_list=news_list)
