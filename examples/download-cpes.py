"""
Script for downloading CPEs

This script downloads CPEs and commits them
into the repo

WARNING: This script will add commits
"""

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import git
from pathlib import Path
import os
import sys
import time
import yaml

from cpe2stix.config import Config
from cpe2stix.main import main
from cpe2stix import logger

EXAMPLES_FOLDER = Path(os.path.abspath(__file__)).parent
REPO_FOLDER = EXAMPLES_FOLDER.parent
CREDENTIALS_FILE_PATH = REPO_FOLDER / "credentials.yml"

STIX2_OBJECTS_FOLDER = REPO_FOLDER / "stix2_objects"
STIX2_BUNDLES_FOLDER = REPO_FOLDER / "stix2_bundles"

repo = git.Repo(REPO_FOLDER)
repo.config_writer().set_value("user", "name", "Signals Corps Bot").release()
repo.config_writer().set_value("user", "email", "github-actions@signalscorps.com").release()


api_key = None
if os.path.exists(CREDENTIALS_FILE_PATH):
    with open(CREDENTIALS_FILE_PATH, "r") as stream:
        try:
            data = yaml.safe_load(stream)
            api_key = data["nvd_api_key"]
        except:
            pass

if len(sys.argv) != 3:
    print("ERROR: Expected 2 args - start date and stop date")

cpe_start_date = None
if sys.argv[1] == "yesterday":
    cpe_start_date = date.today() - timedelta(days=1)
else:
    cpe_start_date = datetime.strptime(sys.argv[1], "%Y-%m-%d")

cpe_end_date = None
if sys.argv[2] == "today":
    cpe_end_date = date.today()
else:
    cpe_end_date = datetime.strptime(sys.argv[2], "%Y-%m-%d")


start_date = cpe_start_date

while start_date < cpe_end_date:

    end_date = min(start_date + relativedelta(months=1), cpe_end_date)

    config = Config(
        cpe_start_date=start_date,
        cpe_end_date=end_date,
        stix2_objects_folder=STIX2_OBJECTS_FOLDER,
        stix2_bundles_folder=STIX2_BUNDLES_FOLDER,
        api_key=api_key,
    )

    main(config)

    repo.git.add("--all")
    count_staged_files = len(repo.index.diff("HEAD"))
    if count_staged_files != 0:
        repo.git.commit(
            "-m",
            f"Add CPEs from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
        )

        logger.info(
            "Commit: Add CPEs from %s to %s",
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
        )
    else:
        logger.info("Skipping commit, since there were no changes to add.")

    start_date = end_date

    if start_date < cpe_end_date:
        time.sleep(5)

