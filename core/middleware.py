from rest_framework.authtoken.models import Token
from django.http import JsonResponse

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization', '')
        parts = auth_header.split(' ')
        # Solo intentar validar tokens DRF (40 chars hex), no JWT (empieza con "eyJ")
        if len(parts) == 2 and parts[0].lower() == 'token':
            token_key = parts[1]
            try:
                token = Token.objects.get(key=token_key)
                request.user = token.user
            except Token.DoesNotExist:
                return JsonResponse({'status': 'fail', 'detail': 'Invalid token.'}, status=401)

        response = self.get_response(request)
        return response
