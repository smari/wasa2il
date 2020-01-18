from django.utils.deprecation import MiddlewareMixin

class LanguageControlMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if 'HTTP_ACCEPT_LANGUAGE' in request.META:
            del request.META['HTTP_ACCEPT_LANGUAGE']
