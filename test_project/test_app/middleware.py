import logging
from django.shortcuts import redirect
from urllib.parse import urlparse

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CustomRefererMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_referer = ['example.com']
        self.ua = ['Mozilla/5.0']
        self.subdomain = 'sub'
        self.blockpage = 'https://google.com'

    def __call__(self, request):
        try:
            referer = request.META.get('HTTP_REFERER', '')
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            current_host = request.get_host()

            if current_host.startswith(self.subdomain + '.') or user_agent in self.ua:
                logger.debug("Already on subdomain or bot, skipping filtering")
                return self.get_response(request)

            else:

                if referer in self.allowed_referer and user_agent not in self.ua:
                    redirect_url = self._build_redirect_url(request)
                    logger.debug(f"Redirecting to {redirect_url} because of valid referer {referer}")
                    return redirect(redirect_url)

                if referer not in self.allowed_referer and user_agent not in self.ua:
                    logger.debug(f"Redirecting to {self.blockpage} because direct visit")
                    return redirect(self.blockpage)

        except Exception as e:
            logger.error(f"An error occurred: {e}")

        return self.get_response(request)

    def _build_redirect_url(self, request):
        parsed_url = urlparse(request.build_absolute_uri())
        netloc = f"{self.subdomain}.{parsed_url.hostname}"
        redirect_url = parsed_url._replace(netloc=netloc).geturl()
        return redirect_url


