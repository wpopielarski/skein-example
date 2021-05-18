import sys
import logging

import argparse
from getpass import getuser

import skein
from skein.tornado import init_kerberos


LOGGER_SETTINGS = {
    "stream": sys.stdout,
    "level": logging.INFO,
    "datefmt": '%Y-%m-%d %H:%M:%S',
    "format": '%(asctime)s %(levelname)s %(message)s'
}

logger = logging.getLogger("distributed.worker")

parser = argparse.ArgumentParser('test Streamz with Yarn and Dask')
parser.add_argument(
    "--keytab", default=None,
    help=("The location of a keytab file. If not specified, 'simple' "
          "authentication will be used")
)
parser.add_argument(
    "--principal", default=None,
    help=("The principal to use if using kerberos. Defaults to the "
          "current user name.")
)

args = parser.parse_args()

init_kerberos(keytab=args.keytab)
# Also create the skein client with keytab and principal specified
skein_client = skein.Client(
    keytab=args.keytab,
    principal=args.principal or getuser()
)


def check_is_shutdown(client, app_id, status="SUCCEEDED"):
    import time
    report = client.application_report(app_id)
    while report.state not in ("FINISHED", "FAILED", "KILLED"):
        time.sleep(0.1)
        report = client.application_report(app_id)

spec = skein.ApplicationSpec.from_file(path='dask_spec.yml', format='yaml')

app_id = skein_client.submit(spec)

check_is_shutdown(skein_client, app_id)

