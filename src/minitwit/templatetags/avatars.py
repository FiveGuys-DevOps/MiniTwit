from hashlib import md5

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter  # by default uses function name, so gravatar_url
@stringfilter
def gravatar_url(email, size=80):
    """Return the gravatar image for the given email address."""
    return "http://www.gravatar.com/avatar/%s?d=identicon&s=%d" % (
        md5(email.strip().lower().encode("utf-8")).hexdigest(),
        size,
    )
