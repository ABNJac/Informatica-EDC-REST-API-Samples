"""
defines a class to help with edc connections & uses requests.session to store
credentials & verify settings for each subsequent api call

will use these env variables, if they exist (default)
    INFA_EDC_URL
    INFA_EDC_AUTH
    INFA_EDC_SSL_PEM

uses command-line args to easily define common connection properties for edc
    these properties will over-ride what is stored in env-vars
    -c --edcurl  http(s)://catalogserver:port
    -a --auth    base64 encoded credentials see encodeUser.py
    -u --user    (not preferred) but can be passed (will prompt for pwd)
    -s --sslcert https certificate if needed

Usage:
    edcSession = EDCSession()
    edcSession.initUrlAndSessionFromEDCSettings()

    ...
    resp = edcSession.session.get(resourceUrl, params=(), timeout=10)

Note: this is syncronyous version - not async
"""
import argparse
import os
import warnings
from urllib.parse import urljoin

import requests

warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# from pathlib import Path
import pathlib
from dotenv import load_dotenv


class EDCSession:
    """
    encapsulates argparse based command-line parser & requests.session object
    for easy re-use for multiple scripts
    """

    def __init__(self):
        self.baseUrl = None
        self.session: requests.session = None
        self.argparser = argparse.ArgumentParser(add_help=False)
        self.__setup_standard_cmdargs__()
        self.edcversion = 0
        self.timeout = 10

    def __setup_standard_cmdargs__(self):
        # check for args overriding the env vars
        self.argparser.add_argument(
            "-c",
            "--edcurl",
            required=False,
            help=(
                "edc url  - including http(s)://<server>:<port>, "
                "if not already configured via INFA_EDC_URL environment var "
            ),
            type=str,
        )
        self.argparser.add_argument(
            "-v",
            "--envfile",
            help=(
                ".env file with config settings INFA_EDC_URL,INFA_EDC_AUTH etc  "
                "will over-ride system environment variables.  "
                "if not specified - '.env' file in current folder will be used "
            ),
            default=".env",
        )
        group = self.argparser.add_mutually_exclusive_group()
        group.add_argument(
            "-a",
            "--auth",
            required=False,
            help=(
                "basic authorization encoded string (preferred over -u) "
                "if not already configured via INFA_EDC_AUTH environment var"
            ),
            type=str,
        )
        group.add_argument(
            "-u",
            "--user",
            required=False,
            help="user name - will also prompt for password ",
            type=str,
        )
        self.argparser.add_argument(
            "-s",
            "--sslcert",
            required=False,
            help=(
                "ssl certificate (pem format), if not already configured "
                "via INFA_EDC_SSL_PEM environment var"
            ),
            type=str,
        )

    def initUrlAndSessionFromEDCSettings(self):
        """
        reads the env vars and any command-line parameters & creates an edc session
        with auth and optionally verify attributes populated (shared so no need to use
        on individual calls)
        returns:
            url, auth
        """
        auth = None
        verify = None

        print("\treading common env/env file/cmd settings")

        args, unknown = self.argparser.parse_known_args()
        if args.envfile is not None:
            # check if the file exists
            # envfullpath = (pathlib.Path(".").cwd() / args.envfile)
            print(f"ready to check .env file {args.envfile}")
            if pathlib.Path(args.envfile).is_file():
                print(f"\t\tloading from .env file {args.envfile}")
                # envfullpath = f"{Path('.').cwd()}\\{args.envfile}"
                # override - ensure we read settings from <envfile> vs vars
                load_dotenv(
                    dotenv_path=(pathlib.Path(args.envfile)),
                    verbose=True,
                    override=True,
                )
                # check the settings from the .env file
                # print(os.getenv("INFA_EDC_URL"))
                if self.baseUrl is None:
                    edcurl = os.getenv("INFA_EDC_URL")
                    print(f"\t\tread edc url from {args.envfile} value={edcurl}")
                    if edcurl is not None and edcurl != self.baseUrl:
                        print(f"\t\treplacing edc url with value from {args.envfile}")
                        self.baseUrl = edcurl
                print("EDCUrl: " + self.baseUrl)
                if auth is None:
                    edcauth = os.environ["INFA_EDC_AUTH"]
                    # print(f"read edc auth from {args.envfile} value={edcauth}")
                    if edcauth is not None and edcauth != auth:
                        print(
                            f"\t\treplacing edc auth with INFA_EDC_AUTH value "
                            "from {args.envfile}"
                        )
                        auth = edcauth
            else:
                print("isfile False")
        else:
            print("env file not found??")
        if "CUSTOM_INFA_EDC_URL" in os.environ:
            self.baseUrl = os.environ["CUSTOM_INFA_EDC_URL"]
            print("\t\tusing EDC_URL=" + self.baseUrl + " from INFA_EDC_URL environment variable")

        if "CUSTOM_INFA_EDC_AUTH" in os.environ:
            print("\t\tusing INFA_EDC_AUTH from environment")
            auth = os.environ["CUSTOM_INFA_EDC_AUTH"]
            # print(f"value = {auth}")

        if "INFA_EDC_SSL_PEM" in os.environ:
            verify = os.environ["INFA_EDC_SSL_PEM"]
            print("\t\tusing ssl certificate from env var INFA_EDC_SSL_PEM=" + verify)

        # check the catalog url & user command-line
        if args.edcurl is not None:
            if self.baseUrl != args.edcurl:
                print(f"\t\tusing edcurl from command-line parameter {args.edcurl}")
                self.baseUrl = args.edcurl
        # if there is still no edc url - then prompt for it
        if self.baseUrl is None:
            # nothing entered anywyere for the base url
            print(f"edc url not specified in ENV var or command-line parameter")

        # user credential stored in auth
        if args.auth is not None:
            print(f"\t\tover-riding auth setting from command-line..{args.auth}")
            auth = args.auth

        # if there is still no auth - then prompt for id and pwd
        if auth is None:
            print(
                f"no credentials in ENV var/.env file/command-line - "
            )

        if args.sslcert is not None:
            if args.sslcert == "False":
                verify = False
            else:
                verify = args.sslcert

        if self.baseUrl is None:
            # prompt the user for the catalog ui

            print(
                "\t\tno catalog url passed, either as env variable or with "
                "-c/--edcurl parameter - exiting"
            )

        # create a session
        self.session = requests.Session()
        # session.headers.update({"Accept": "application/json"})
        self.session.verify = verify
        self.session.headers.update({"Authorization": auth})
        self.session.baseUrl = self.baseUrl

        print("\tfinished reading common env/.env/cmd parameters")

    def initSession(self, catalog_url, catalog_auth, verify):
        """
        given a valid URL and auth - setup a requests session to use
        for subsequent calls, verify can be False
        """
        self.session = requests.Session()
        self.baseUrl = catalog_url
        self.session.baseUrl = self.baseUrl
        self.session.headers.update({"Authorization": catalog_auth})
        if verify is None:
            verify = False
        self.session.verify = verify

    def validateConnection(self):
        """
        validate that the connection informatioon (url + auth credentials)
        are correct.
        returns:
            status code (e.g. 200 for ok)
            json message ()
        """
        print(f"validating connection to {self.session.baseUrl}")
        try:
            url = urljoin(self.baseUrl, "access/2/catalog/data/productInformation")
            # url = self.baseUrl + "access/2/catalog/data/productInformation"
            resp = self.session.get(url, timeout=self.timeout)
            print(f"\tapi status code={resp.status_code}")
            if resp.status_code == 200:
                # valid and 10.4+, get the actual version
                rel_version = resp.json().get("releaseVersion")
                if rel_version.count(".") == 2:
                    # version is something like 10.4.0
                    # but we need to make it a 4 part name like 10.4.0.0
                    rel_version = rel_version + ".0"
                # remove the "." from the version
                rel_nbr = int(rel_version.replace(".", ""))
                self.edcversion = rel_nbr
                # print(f"release version={rel_version} {rel_nbr}")
                return resp.status_code, resp.json()
            elif resp.status_code == 400:
                print("catalog server is not v10.4 or later - trying another method...")
                # invalid request - try another api call
                url = urljoin(self.baseUrl, "access/1/catalog/data")
                resp = self.session.get(url, timeout=3)
                print(f"\t2nd try status code = {resp.status_code}")
            else:
                print(f"error connecting {resp.json()}")
            return resp.status_code, resp.json()
        except requests.exceptions.RequestException as e:
            print("Error connecting to : " + self.session.baseUrl)
            print(e.strerror)
            # exit if we can't connect
            return 0, None

    def main(self):
        print("Main should not be called for edcSessionHelper...")
        return 1
    

if __name__ == "__main__":
    result = EDCSession().main()
