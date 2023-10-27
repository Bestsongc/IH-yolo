# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/10/17 15:10
# @File    : json_response.py
# @Software: PyCharm
import json
from flask import Response

class JsonResponse:
    '''
    用于返回json格式的数据
    '''
    class HttpResponseStatus:
        SUCCESS = 200
        FAILED = 400
        AUTHORIZATION_FAILURE = 401
        ACCESS_DENIED = 403
        ERROR = 500
        NOT_FOUND = 404

        @classmethod
        def find_status_by_status_code(cls, code):
            for _, value in cls.__dict__.items():
                if value == code:
                    return value
            return None

    def __init__(self, msg="no msg", status=HttpResponseStatus.SUCCESS, content=None):
        self.status = status
        self.msg = msg
        self.content = content

    def to_string(self):
        response_data = {
            "status": self.status,
            "msg": self.msg
        }
        if self.content:
            response_data["content"] = self.content
        response_json = json.dumps(response_data)
        return Response(response_json, content_type='application/json')

    @staticmethod
    def success(data=None, msg="no msg"):
        return JsonResponse(msg, JsonResponse.HttpResponseStatus.SUCCESS, data).to_string()

    @staticmethod
    def fail(msg="error", code=HttpResponseStatus.ERROR):
        return JsonResponse(msg, code).to_string()

if __name__ == '__main__':
    # Example usage:
    response = JsonResponse.success(data=None,msg= "operation successful")
    print(response)
