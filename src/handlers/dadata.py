from flask import request
from flask_restx import Resource

from src.services.dadata.dadata import suggest_company_by_inn
from src.swagger_schemas.swagger_models import dadata_ns


@dadata_ns.route("/suggest")
class SuggestInn(Resource):
    def post(self):
        data = request.get_json()
        query = data.get("query")
        if not query:
            return {"message": "Не передан ИНН или название"}, 400

        suggestion = suggest_company_by_inn(query)
        if not suggestion:
            return {"message": "Ничего не найдено"}, 404

        return suggestion, 200
