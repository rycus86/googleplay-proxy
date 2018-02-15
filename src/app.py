import logging
import os

from flask import Flask, jsonify
from flask_cache import Cache
from flask_cors import CORS

from prometheus_flask_exporter import PrometheusMetrics
from docker_helper import read_configuration

from api import ApiClient
from scraper import Scraper

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
metrics = PrometheusMetrics(app)

metrics.info('flask_app_info', 'Application info',
             version=os.environ.get('GIT_COMMIT') or 'unknown')

metrics.info(
    'flask_app_built_at', 'Application build timestamp'
).set(
    float(os.environ.get('BUILD_TIMESTAMP') or '0')
)

CORS(app, origins=read_configuration(
    'CORS_ORIGINS', '/var/secrets/secrets.env', default='http://localhost:?.*'
).split(','), methods='GET')

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(module)s.%(funcName)s - %(message)s')
logger = logging.getLogger('googleplay-proxy')
logger.setLevel(logging.INFO)


def load_api():
    api_type = read_configuration('API_TYPE', '/var/secrets/secrets.env', default='api')

    if api_type == 'api':
        return ApiClient(
            android_id=read_configuration('ANDROID_ID', '/var/secrets/secrets.env'),
            username=read_configuration('GOOGLE_USERNAME', '/var/secrets/secrets.env'),
            password=read_configuration('GOOGLE_PASSWORD', '/var/secrets/secrets.env'),
            max_login_retries=int(read_configuration(
                'MAX_LOGIN_RETRIES', '/var/secrets/secrets.env', default='10'
            ))
        )

    elif api_type == 'scraper':
        return Scraper(cache_max_age=int(
            read_configuration('MAX_CACHE_AGE', '/var/secrets/secrets.env', default=24 * 60 * 60)
        ))

    else:
        logger.error('Invalid API type "%s" (valid ones are: "api" and "scraper")', os.environ.get('API_TYPE'))
        exit(1)


api = load_api()


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
