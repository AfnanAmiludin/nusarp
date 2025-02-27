class IFrameMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Deteksi apakah request dari iframe
        request.is_iframe = request.GET.get('iframe', 'false') == 'true'
        return self.get_response(request)