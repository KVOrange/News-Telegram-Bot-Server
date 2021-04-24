from flask import Blueprint, request
from pydantic import BaseModel

from app.handlers.json_handler import get_response
from app.models import User, db

module = Blueprint('users', __name__, url_prefix='/users')


class RegData(BaseModel):
    name: str
    telegram_id: int


@module.route('/', methods=['POST'])
def registration():
    try:
        req_data = RegData.parse_raw(request.data)
    except ValueError as error:
        return get_response(400, False, 'Проверьте правильность запроса', data=error.errors())
    if User.query.filter_by(telegram_id=req_data.telegram_id).first():
        return get_response(400, False, 'Пользователь уже существует')
    new_user = User(name=req_data.name, telegram_id=req_data.telegram_id)
    db.session.add(new_user)
    db.session.commit()
    return get_response(400, False, '', user_id=new_user.id)
