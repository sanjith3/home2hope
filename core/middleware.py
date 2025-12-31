from django.utils.cache import add_never_cache_headers

class DisableBrowserCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Only disable cache for authenticated users to ensure security
        # but allow public pages to be cached if needed.
        # Alternatively, disable for everything if privacy is paramount.
        if request.user.is_authenticated:
            add_never_cache_headers(response)
        
        return response
