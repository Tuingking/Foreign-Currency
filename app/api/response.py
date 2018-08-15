from flask import json, Response


def api_response(data=[], **kwargs):
    status = kwargs.get('status', 200)
    message = kwargs.get('message', '')
    reason = kwargs.get('reason', '')
    error = kwargs.get('error', None)

    if error:
        message = reason = error

    res = {
        "header": {
            "status": status,
            "message": message,
            "reason": reason
        },
        "data": data
    }
    return Response(status=status,
                    response=json.dumps(res),
                    mimetype='application/json')


class HttpResponse:

    @staticmethod
    def invalid_payload():
        return api_response(status=400, message="INVALID PAYLOAD")

    @staticmethod
    def bad_request():
        return api_response(status=400, message="BAD REQUEST")

    @staticmethod
    def not_found():
        return api_response(status=404, message="NOT FOUND")

    @staticmethod
    def created():
        return api_response(status=201, message="CREATED")
