"""
Basic views to allow browsing of the YAMLCONF definitions.
"""
import logging
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from django.shortcuts import render
from yamlconfig import get_cached_attributes
from yamlconfig import get_attr_info

logger = logging.getLogger(__name__)


@staff_member_required
def index(request):
    """
    Generate the main page listing the YAMLCONF definitions.
    """
    title = 'YAMLCONF Attributes'
    logger.debug("Generating index page for YAMLCONF")
    return render(
        request,
        "yamlconfig/index.html",
        {'attrs': get_cached_attributes(), 'title': title}
    )


@staff_member_required
def attr_info(request, name):
    """
    Display the page giving information on an individual attribute.
    """
    title = 'YAMLCONF: "{0}" Attribute'.format(name)
    logger.debug("Generating YAMLCONF info page for \"%s\"", name)
    info = get_attr_info(name)
    if info is None:
        logger.info("No such YAMLCONF attribute \"%s\"", name)
        raise Http404
    return render(
        request,
        "yamlconfig/attribute.html",
        {'name': name, 'info': info, 'title': title}
    )
