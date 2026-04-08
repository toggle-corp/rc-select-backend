from django import template
from django.conf import settings
from django.templatetags.static import static

register = template.Library()


@register.filter(is_safe=True)
def static_full_path(path):
    static_path = static(path)
    # Domain from URL object
    domain = f"{settings.APP_DOMAIN.scheme}://{settings.APP_DOMAIN.hostname}"
    if settings.APP_DOMAIN.port:
        domain += f":{settings.APP_DOMAIN.port}"
    return f"{domain}{static_path}"
