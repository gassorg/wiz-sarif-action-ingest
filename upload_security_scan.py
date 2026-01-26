import argparse
import traceback
from contextlib import closing
import json
import os.path
import errno
import os
import signal
import functools
import requests
import logging
import time

"""
README
------
Disclaimer
By using this software and associated documentation files (the "Software") you hereby agree and understand that:
The use of the Software is free of charge and may only be used by Wiz customers for its internal purposes.
The Software should not be distributed to third parties.
The Software is not part of Wiz's Services and is not subject to your company's services agreement with Wiz.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL WIZ BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE USE OF THIS SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

REF - https://docs.wiz.io/dev/script-upload-security-scan-file
"""

# -------------------------------------------------------
# CONFIG DEFAULTS (can be overridden by config.json)
# -------------------------------------------------------

CLIENT_ID = ""
CLIENT_SECRET = ""
TOKEN_URL = ""  # e.g. https://auth.app.wiz.io/oauth/token
API_ENDPOINT_URL = ""  # e.g. https://api.us17.app.wiz.io/graphql

FILE_ABSOLUTE_PATH = ""  # e.g. /Users/Desktop/upload-scan.json
ENTITY_TYPE = ["VIRTUAL_MACHINE"]

# Logger
logger = logging.getLogger('')
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


class TimeoutError(Exception):
    pass


def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wrapper

    return decorator


class WizApi:
    COGNITO_URLS = [
        'https://auth.app.wiz.io/oauth/token',
        'https://auth.gov.wiz.io/oauth/token',
        'https://auth.test.wiz.io/oauth/token',
        'https://auth.demo.wiz.io/oauth/token'
    ]

    SESSION = ''
    WIZ_API_URL = ''
    general_max_retries = 0
    general_retry_time = 0
    DEFAULT_VALUE = 'N/A'

    # Queries
    CLOUD_RESOURCE_SEARCH_QUERY = ("""
        query CloudResourceSearch(
            $filterBy: CloudResourceFilters
            $first: Int
            $after: String
        ) {
            cloudResources(
                filterBy: $filterBy
                first: $first
                after: $after
            ) {
                nodes {
                    ...CloudResourceFragment
                }
                pageInfo {
                    hasNextPage
                    endCursor
                }
            }
        }
        fragment CloudResourceFragment on CloudResource {
            id
            name
            type
            subscriptionId
            subscriptionExternalId
            graphEntity {
                id
                providerUniqueId
                name
                type
                projects { id }
                properties
                firstSeen
                lastSeen
            }
        }
    """)

    CLOUD_RESOURCE_SEARCH_VARIABLES = {
        "first": 500,
        "filterBy": {"type": ["VIRTUAL_MACHINE"]}
    }

    REQUEST_SECURITY_SCAN_UPLOAD_QUERY = ("""
        query RequestSecurityScanUpload($filename: String!) {
            requestSecurityScanUpload(filename: $filename) {
                upload {
                    id
                    url
                    systemActivityId
                }
            }
        }
    """)

    REQUEST_SECURITY_SCAN_UPLOAD_VARIABLE = {
        "input": {
            "filename": None
        }
    }

    SYSTEM_ACTIVITY_QUERY = ("""
query SystemActivity($id: ID!) {
    systemActivity(id: $id) {
        id
        status
        statusInfo
    }
}
    """)

    SYSTEM_ACTIVITY_VARIABLES = {"id": None}

    def set_api_endpoint(self, api_endpoint):
        self.api_endpoint_url = api_endpoint

    def set_session(self, session):
        self.session = session

    def init(self, client_id, client_secret, auth_url):
        auth_data = self._select_authentication_provider(client_id, client_secret, auth_url)
        response = requests.post(auth_url,
                                 headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                 data=auth_data)
        if response.status_code != requests.codes.ok:
            raise Exception(f'Error authenticating to Wiz [{response.status_code}] - {response.text}')

        response_json = response.json()
        access_token = response_json.get('access_token')
        if not access_token:
            raise Exception(f'Could not retrieve token from Wiz: {response_json.get("message")}')
        return access_token

    def _select_authentication_provider(self, client_id, client_secret, tenant_auth_url):
        if tenant_auth_url in self.COGNITO_URLS:
            return {'grant_type': 'client_credentials', 'audience': 'wiz-api',
                    'client_id': client_id, 'client_secret': client_secret}
        else:
            raise Exception('Invalid Auth URL')

    def query(self, query, variables):
        response = self.session.post(self.api_endpoint_url,
                                     json={'variables': variables, 'query': query})
        if response.status_code != requests.codes.ok:
            raise Exception('Error authenticating to Wiz [{}] - {}'.format(response.status_code, response.text))
        response_json = response.json()
        data = response_json.get('data')
        if not data:
            raise Exception('Could not get entries from Wiz: {}'.format(response_json.get('errors')))
        return data


wiz_api_client = WizApi()


def get_token(client_id, client_secret, token_url):
    return wiz_api_client.init(client_id, client_secret, token_url)


def validate_json_structure_and_return_value(json_file, struct_list):
    return_values = []
    for struct in struct_list:
        json_tree_var = json_file
        for element in struct:
            json_tree_var = json_tree_var[element]
        return_values.append(json_tree_var)
    return return_values


def get_cloud_resource():
    logging.info('# Step 1 - Fetch Cloud Resources')
    cloud_resource_variables = wiz_api_client.CLOUD_RESOURCE_SEARCH_VARIABLES
    cloud_resource_result = wiz_api_client.query(
        wiz_api_client.CLOUD_RESOURCE_SEARCH_QUERY,
        cloud_resource_variables
    )
    logging.info('# Step 1 - Successfully Fetched Cloud Resources')
    return cloud_resource_result


def create_new_file_path_containing_wiz_assets_information(wiz_inventory_content, file_path):
    logging.info('# Step 2 - Enrich Cloud Resources')
    new_file_path = file_path
    logging.info('# Step 2 - Successfully Enriched Cloud Resources')
    return new_file_path


def upload_file_request(wiz_info_file_path):
    logging.info(f'# Step 3 - Upload File Request for {wiz_info_file_path}')
    upload_request_variables = wiz_api_client.REQUEST_SECURITY_SCAN_UPLOAD_VARIABLE
    upload_request_variables["filename"] = os.path.split(wiz_info_file_path)[-1]

    upload_response = wiz_api_client.query(
        wiz_api_client.REQUEST_SECURITY_SCAN_UPLOAD_QUERY,
        upload_request_variables
    )

    upload_id, upload_url, system_activity_id = validate_json_structure_and_return_value(
        upload_response,
        [["requestSecurityScanUpload", "upload", "id"],
         ["requestSecurityScanUpload", "upload", "url"],
         ["requestSecurityScanUpload", "upload", "systemActivityId"]]
    )

    logging.info('# Step 3 - Upload File Request successful')
    return upload_url, system_activity_id


def upload_file_to_s3(url, file_path):
    logging.info(f'# Step 4 - Upload {file_path} to S3')

    with open(file_path) as object_file:
        object_text = object_file.read()

    response = requests.put(url, data=object_text)
    if response.status_code != 200:
        raise Exception(f'Error uploading {file_path}: {response.status_code} - {response.text}')

    logging.info('# Step 4 - Upload successful')


def get_system_activity_status(system_activity_id):
    logging.info('# Step 5 - Checking System Activity')

    system_activity_variables = wiz_api_client.SYSTEM_ACTIVITY_VARIABLES
    system_activity_variables["id"] = system_activity_id

    status = None

    while status not in ("SUCCESS", "FAILURE", "SKIPPED"):
        result = wiz_api_client.query(
            wiz_api_client.SYSTEM_ACTIVITY_QUERY,
            system_activity_variables
        )

        activity = result.get("systemActivity")

        #print(f'result: {result}')

        # Activity not ready yet
        if activity is None:
            logging.info("System Activity not ready yet... retrying in 3 seconds")
            time.sleep(3)
            continue

        status = activity.get("status")

        logging.info(f"Current status: {status}")

        # Not finished yet
        if status not in ("SUCCESS", "FAILURE", "SKIPPED"):
            time.sleep(3)

    logging.info(f'# Step 5 complete: {status}')
    if status != "SUCCESS":
        print(f'System Activity ended with status: {status} and with result: {result}')
    else:
        logging.info('System Activity completed successfully')
        print(f'System Activity ended with status: {status} and with result: {result}')
    return status



def load_config(filename):
    with open(filename, 'r') as config_file:
        return json.load(config_file)


def main():
    try:
        parser = argparse.ArgumentParser(description='Upload security files to Wiz')
        parser.add_argument('-c', '--config_file', type=str, help='Path to config JSON')
        parser.add_argument('-f', '--file_path', type=str, help='Path to enrichment JSON')
        args = parser.parse_args()

        # ---------------------------------------
        # CONFIG BRANCH
        # ---------------------------------------
        if args and any(vars(args).values()):
            if not os.path.isfile(args.config_file):
                raise Exception(f'Config file "{args.config_file}" not found.')

            if not os.path.isfile(args.file_path):
                raise Exception(f'File path "{args.file_path}" not found.')

            config = load_config(args.config_file)

            client_id = config.get("CLIENT_ID", CLIENT_ID)
            client_secret = config.get("CLIENT_SECRET", CLIENT_SECRET)
            token_url = config.get("TOKEN_URL", TOKEN_URL)
            api_endpoint = config.get("API_ENDPOINT_URL", API_ENDPOINT_URL)

            file_path = args.file_path

            token = get_token(client_id, client_secret, token_url)

        else:
            # ---------------------------------------
            # FALLBACK BRANCH
            # ---------------------------------------
            token = get_token(CLIENT_ID, CLIENT_SECRET, TOKEN_URL)
            api_endpoint = API_ENDPOINT_URL
            file_path = FILE_ABSOLUTE_PATH

        # ---------------------------------------
        # AUTH & EXECUTION
        # ---------------------------------------
        with requests.Session() as session:
            session.headers.update({
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            })
            wiz_api_client.session = session
            wiz_api_client.api_endpoint_url = api_endpoint

            # Step 1
            wiz_inventory_content = get_cloud_resource()

            # Step 2
            wiz_info_file_path = create_new_file_path_containing_wiz_assets_information(
                wiz_inventory_content, file_path)

            # Step 3
            upload_url, system_activity_id = upload_file_request(wiz_info_file_path)

            # Step 4
            upload_file_to_s3(upload_url, wiz_info_file_path)

            # Step 5
            get_system_activity_status(system_activity_id)

        logging.info('Script completed successfully')
        exit(0)

    except Exception as e:
        print(f'An unexpected error occurred.\nDetails: {str(e)}')
        print(traceback.format_exc())
        exit(1)


if __name__ == '__main__':
    main()