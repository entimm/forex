import os

from flask import Flask, render_template

from app_cache import cache
from common.const import MENUS
from common.utils import create_link

app = Flask(__name__, template_folder='web/templates', static_folder='web/public/static')

app.config['CACHE_TYPE'] = 'simple'
cache.init_app(app)


controllers = [
    'index',
    'chart',
    'backtest',
]

for controller in controllers:
    blueprint = __import__(f'controllers.{controller}_controller', fromlist=['blueprint']).blueprint
    app.register_blueprint(blueprint)


@app.context_processor
def inject_layout_vars():
    return {
        'menus': MENUS,
        'create_link': create_link,
    }


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', **{'error': error}), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html', **{'error': error}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 9999))
    app.run(debug=os.environ.get("DEBUG", True), host='0.0.0.0', port=port)
