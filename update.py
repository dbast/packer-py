#!/usr/bin/env python
import configparser
import hashlib
import logging
import re
import sys
import urllib.request
from pathlib import Path

from packaging.version import Version

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

SETUP_CFG_PATH = Path("setup.cfg")
README_PATH = Path("README.md")
USER_AGENT = "generic-update-script/urllib"


def download_and_hash(url):
    logging.info(f"Hashing: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as response:
        data = response.read()
    sha256_hash = hashlib.sha256(data).hexdigest()
    logging.info(f"  -> SHA256: {sha256_hash}")
    return sha256_hash


def update_setup_cfg(setup_cfg, upstream_version, new_version, url_pattern, url_repl):
    text = setup_cfg.read_text().splitlines(keepends=True)
    url_re = re.compile(r"(?P<indent>\s*url\s*=\s*)(?P<url>.+)")
    sha_re = re.compile(r"(\s*sha256\s*=\s*)(?P<old>[0-9a-f]+)")
    version_re = re.compile(r"^version\s*=\s*(.+)")
    last_url = None
    version_updated = False

    def replace_line(line):
        nonlocal last_url, version_updated
        if not version_updated and (m := version_re.match(line)):
            version_updated = True
            return f"version = {new_version}\n"
        if m := url_re.match(line):
            last_url = re.sub(url_pattern, url_repl.format(version=upstream_version), m.group("url").strip())
            return f"{m.group('indent')}{last_url}\n"
        if last_url and (m := sha_re.match(line)):
            sha, last_url = download_and_hash(last_url), None
            return f"{m.group(1)}{sha}\n"
        return line

    setup_cfg.write_text("".join(map(replace_line, text)))


def update_readme(readme, new_version):
    text = readme.read_text()
    updated_text = re.sub(r"(rev:\s*)\d+\.\d+\.\d+\.\d+", rf"\g<1>{new_version}", text, count=1)
    if updated_text != text:
        logging.info(f"Updating {readme}")
        readme.write_text(updated_text)


def main(setup_cfg=SETUP_CFG_PATH, readme=README_PATH):
    config = configparser.ConfigParser()
    config.read(setup_cfg)
    meta, update = config["metadata"], config["update_settings"]

    hook_version = meta["version"]
    upstream_version = update["version"].lstrip("v")
    new_version = (
        f"{upstream_version}.0" if Version(upstream_version) > Version(hook_version) else hook_version
    )
    logging.info(f"Updating to {new_version}")

    update_readme(readme, new_version)

    if Version(new_version) > Version(hook_version):
        update_setup_cfg(setup_cfg, upstream_version, new_version, update["url_pattern"], update["url_repl"])
    else:
        logging.info(f"Nothing to do: {new_version}<={hook_version}")

    logging.info("--- Update Script Finished ---")
    return 0


if __name__ == "__main__":
    sys.exit(main())
