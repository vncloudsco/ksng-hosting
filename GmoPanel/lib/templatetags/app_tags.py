from django import template
import os
from django.conf import settings
import uuid
register = template.Library()

@register.filter
def render_html(int):
    if (int < 50):
        color = "#00a65a"
    elif(int >= 50 and int < 75):
        color = "#f39c12"
    else:
        color = "#dd4b39"
    inputChart = '<input class="knob" data-angleOffset=-125 data-angleArc=250 data-fgColor="{}" value="{}" data-readOnly=true>'.format(color,int)

    return inputChart

@register.simple_tag(name='cache_bust')
def cache_bust():

    if settings.DEBUG:
        version = uuid.uuid1()
    else:
        version = os.environ.get('PROJECT_VERSION')
        if version is None:
            version = '1'

    return '__v__={version}'.format(version=version)