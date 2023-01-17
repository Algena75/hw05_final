from django.utils import timezone


def year(request):
    """Объявляем переменную с текущим годом."""
    return {
        'c_p_year': timezone.now().year,
    }
