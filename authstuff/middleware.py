class NameMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        if request.user.is_authenticated:
            request.username = request.user.username
            request.session["name"] = None
        elif "name" in request.session and request.session["name"]:
            request.username = "guest-%s" % request.session["name"]
        else:
            request.username = None

        response = self.get_response(request)
        return response
