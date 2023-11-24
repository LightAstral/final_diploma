from django.shortcuts import redirect
from django.contrib import messages


class DomainPurchaseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == 'purchase_domain':
            if not request.user.is_authenticated:
                messages.warning(request, 'Для покупки домена необходимо зарегестрироваться.')
                return redirect('login')
        return self.get_response(request)
