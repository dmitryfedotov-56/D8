from django import template

register = template.Library()


@register.filter(name='appearance')              # post type appearance
def type_appearance(p_type, default_line):
    if p_type == 'AR': return 'Статья'
    if p_type == 'NW': return 'Новость'


BLACK_LIST = [                                  # forbidden words
    'плохое',
]


@register.filter(name='censor')                 # forbidden word replacement
def censor(value, line_to_show):
    s = value
    for word in BLACK_LIST: s = s.replace(word, line_to_show)
    return s




