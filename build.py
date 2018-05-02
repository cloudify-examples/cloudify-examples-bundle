########
# Copyright (c) 2018 Cloudify Platform Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import requests
import shutil
import sys
import tarfile
import tempfile
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

EXAMPLES_YAML = os.path.join(os.path.dirname(__file__), 'examples.yaml')
USAGE = "Usage: `python build.py [Cloudify Version] [output directory]`.\n"


def read_examples_yaml(yaml_path=EXAMPLES_YAML):
    with open(yaml_path, 'r') as infile:
        return load(infile.read(), Loader=Loader)


def get_download_urls(_examples, version):
    return [ex['versions'][version] for ex in _examples if version in ex['versions']]


def download_archives(directory, url_list):
    for url in url_list:
        filepath = \
            os.path.join(directory, url.split("/")[-3])
        print "Writing file {0}".format('{0}.tar.gz'.format(filepath))
        with open('{0}.tar.gz'.format(filepath), "wb") as outfile:
            response = requests.get(url)
            outfile.write(response.content)
    return directory


def create_tarfile(directory, tarfile_path):
    old_dir = os.getcwd()
    os.chdir(directory)
    with tarfile.open(tarfile_path, "w:gz") as outtar:
        for file in os.listdir('.'):
            outtar.add(file)
    os.chdir(old_dir)
    shutil.rmtree(directory)


if __name__ == '__main__':
    print "Starting Cloudify Examples Bundle Build"

    try:
        cfy_version = sys.argv[1]
    except IndexError:
        print USAGE
        exit(1)

    try:
        output_directory = sys.argv[2]
    except IndexError:
        print USAGE
        output_directory = os.getcwd()
        print "Non-fatal error: Using output directory {0}\n".format(output_directory)

    examples_yaml = read_examples_yaml()
    if cfy_version not in examples_yaml['cloudify-versions']:
        print "Error: Version {0} does not have a bundle configured".format(cfy_version)
        sys.exit(1)

    urls = get_download_urls(examples_yaml['examples'], cfy_version)

    if not len(urls):
        print "Error: there are no downloads for version {0}".format(cfy_version)
        sys.exit(1)

    directory_to_archive = download_archives(tempfile.mkdtemp(), urls)
    tarfile_path = os.path.join(
        output_directory,
        "examples-bundle-{0}.tar.gz".format(cfy_version))
    create_tarfile(directory_to_archive, tarfile_path)
    print "Wrote {0}".format(tarfile_path)
