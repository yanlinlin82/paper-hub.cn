import json
from django.utils.deprecation import MiddlewareMixin

class JsonBodyMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.content_type == 'application/json':
            try:
                request.json_data = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError:
                request.json_data = None
