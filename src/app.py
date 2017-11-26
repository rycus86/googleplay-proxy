import logging
import os

from flask import Flask, jsonify
from flask_cache import Cache
from flask_cors import CORS

from prometheus_flask_exporter import PrometheusMetrics

from api import ApiClient
from scraper import Scraper

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
metrics = PrometheusMetrics(app)

metrics.info('flask_app_info', 'Application info',
             version=os.environ.get('GIT_COMMIT', 'unknown'))

metrics.info(
    'flask_app_built_at', 'Application build timestamp'
).set(
    float(os.environ.get('BUILD_TIMESTAMP', '0'))
)

CORS(app, origins=os.environ.get('CORS_ORIGINS', 'http://localhost:?.*').split(','), methods='GET')

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(module)s.%(funcName)s - %(message)s')
logger = logging.getLogger('googleplay-proxy')
logger.setLevel(logging.INFO)

if os.environ.get('API_TYPE', 'api') == 'api':
    api = ApiClient(android_id=os.environ.get('ANDROID_ID'),
                    username=os.environ.get('GOOGLE_USERNAME'),
                    password=os.environ.get('GOOGLE_PASSWORD'),
                    max_login_retries=int(os.environ.get('MAX_LOGIN_RETRIES', '10')))

elif os.environ.get('API_TYPE', 'api') == 'scraper':
    api = Scraper(cache_max_age=int(os.environ.get('MAX_CACHE_AGE', 24 * 60 * 60)))

else:
    logger.error('Invalid API type "%s" (valid ones are: "api" and "scraper")', os.environ.get('API_TYPE'))
    exit(1)


@app.route('/search/<package_prefix>')
@cache.memoize(timeout=3600)
def search_applications(package_prefix):
    logger.info('Searching application with package prefix: %s', package_prefix)
    return jsonify(api.search(package_prefix))


@app.route('/developer/<developer_name>')
@cache.memoize(timeout=3600)
def search_developer(developer_name):
    logger.info('Searching application with developer name: %s', developer_name)
    return jsonify(api.developer(developer_name))


@app.route('/details/<package_name>')
@cache.memoize(timeout=3600)
def get_application_details(package_name):
    logger.info('Fetching application details for package: %s', package_name)
    return jsonify(api.get_details(package_name))


if __name__ == '__main__':  # pragma: no cover
    app.run(host=os.environ.get('HTTP_HOST', '127.0.0.1'),
            port=int(os.environ.get('HTTP_PORT', '5000')),
            threaded=True, debug=False)
