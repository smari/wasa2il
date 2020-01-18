class CookiesDirectiveMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_response(self, request, response):
        # Prevent cookies from being set, unless the user has specifically
        # consentend to their use.
        if request.COOKIES.get('cookiesDirective') != '1':
            response.cookies.clear()

        return response
