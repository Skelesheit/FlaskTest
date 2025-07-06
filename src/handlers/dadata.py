from flask import request
from flask_restx import Resource

from src.services.dadata.dadata import suggest_company_by_inn
from src.swagger_schemas.swagger_models import dadata_ns


@dadata_ns.route("/suggest/<string:inn>")
class SuggestInn(Resource):
    def get(self, inn: str):
        if not inn.isdigit() or not (10 <= len(inn) <= 12):
            return {"message": "Некорректный ИНН"}, 400
        suggestion = suggest_company_by_inn(inn)
        if not suggestion:
            return {"message": "Ничего не найдено"}, 404
        return suggestion, 200
