import os
import logging
from flask import Flask, jsonify, make_response
from flask_cache import Cache
from api import ApiClient

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

api = ApiClient(android_id=os.environ.get('ANDROID_ID'),
                username=os.environ.get('GOOGLE_USERNAME'),
                password=os.environ.get('GOOGLE_PASSWORD'),
                max_login_retries=int(os.environ.get('MAX_LOGIN_RETRIES', '10')))

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(module)s.%(funcName)s - %(message)s')
logger = logging.getLogger('googleplay-proxy')
logger.setLevel(logging.INFO)


@app.route('/search/<package_prefix>')
@cache.memoize(timeout=3600)
def search_applications(package_prefix):
    logger.info('Searching application with package prefix: %s', package_prefix)
    return jsonify(api.search(package_prefix))


@app.route('/details/<package_name>')
@cache.memoize(timeout=3600)
def get_application_details(package_name):
    logger.info('Fetching application details for package: %s', package_name)
    return jsonify(api.get_details(package_name))


if __name__ == '__main__':
    app.run(host=os.environ.get('HTTP_HOST', '127.0.0.1'),
            port=int(os.environ.get('HTTP_PORT', '5000')),
            debug=False)
