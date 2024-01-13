from collections import defaultdict

from flask import Blueprint, render_template, request, url_for, redirect

from app_cache import cache
from common.const import MENUS
from controllers import make_cache_key

blueprint = Blueprint('index', __name__)


@blueprint.route('/')
@cache.cached(timeout=12 * 60 * 60, key_prefix=make_cache_key)
def index():
    grouped_menus = defaultdict(list)
    for item in MENUS:
        grouped_menus[item['type']].append(item)
    grouped_menus = dict(grouped_menus)

    return render_template('index.html', **{'grouped_menus': grouped_menus})


@blueprint.route('/clear_cache')
def clear_cache():
    cache.clear()

    referrer = request.referrer or url_for('index.index')

    return redirect(referrer)
