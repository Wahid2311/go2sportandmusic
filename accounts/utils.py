from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

User = get_user_model()


def authenticate_via_id_token(request):
    if hasattr(request, 'META'):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    else:
        auth_header = request.request.META.get('HTTP_AUTHORIZATION', '')

    if not auth_header.startswith('Token '):
        return None

    token = auth_header.split(' ')[1].strip()
    if not token:
        return None

    try:
        user = User.objects.get(id=token)
        if user.is_active:
            return user
        else:
            return None
    except (User.DoesNotExist, ValueError):
        return None


def api_login_required(view_func):

    def wrapper(request, *args, **kwargs):
        if hasattr(request, 'META'):
            user = authenticate_via_id_token(request)
        else:
            user = authenticate_via_id_token(request.request)

        if user is None:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        if hasattr(request, 'request'):
            request.request.user = user
        else:
            request.user = user
        return view_func(request, *args, **kwargs)

    return wrapper


def require_user_type(user_type):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.user_type != user_type:
                return JsonResponse({'error': f'Access restricted to {user_type} users'}, status=403)
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator