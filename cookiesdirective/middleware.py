class CookiesDirectiveMiddleware(object):
    def __init__(self):
        pass

    def process_response(self, request, response):
        # Prevent cookies from being set, unless the user has specifically
        # consentend to their use.
        if request.COOKIES.get('cookiesDirective') != '1':
            response.cookies.clear()

        return response
