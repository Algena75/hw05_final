from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator


def page_obj_return(request, posts):
    """Получение page_obj с паджинатором."""
    cache.clear()
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
