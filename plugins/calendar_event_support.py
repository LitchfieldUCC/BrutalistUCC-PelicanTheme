from datetime import datetime
from operator import methodcaller
from itertools import groupby

from pelican import signals
from jinja2 import environmentfilter
from jinja2.filters import _GroupTuple


def _vtext_converter(value):
    if hasattr(value, 'to_ical'):
        return (methodcaller('to_ical')(value)).decode('utf-8')
    else:
        return value


def do_vtext(value):
    if isinstance(value, list):
        value = '\n\n'.join([
            _vtext_converter(x) for x in value
        ])
    value = value.replace('\n\n', '<br>')
    return value


def do_start(value):
    _map = methodcaller('strftime', '%Y%m%d')
    start = value.get('dtstart')
    return _map(start)


@environmentfilter
def do_sortby_start(environment, value):
    return sorted(value, key=do_start)


@environmentfilter
def do_groupby_start(environment, value):
    return [
        _GroupTuple(key, list(values))
        for key, values in groupby(sorted(value, key=do_start), do_start)
    ]


def test_datetime(value):
    return (
        type(value) == datetime
    )


def add_filters(pelican):
    pelican.env.filters.update({ 'vtext'         : do_vtext         })
    pelican.env.filters.update({ 'start'         : do_start         })
    pelican.env.filters.update({ 'sortby_start'  : do_sortby_start  })
    pelican.env.filters.update({ 'groupby_start' : do_groupby_start })


def add_tests(pelican):
    pelican.env.tests.update({ 'datetime' : test_datetime })


def register():
    signals.generator_init.connect(add_filters)
    signals.generator_init.connect(add_tests)