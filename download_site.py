#!/Users/xchen/venv/bin/python

# coding: utf-8
import argparse

import pyaem
from pyaem.exception import PyAemException

parser = argparse.ArgumentParser(description='Download a site from AC.')
parser.add_argument('--sshTunnelPort', default='6789')
parser.add_argument('--site')
parser.add_argument('--locale')
parser.add_argument('--contentRoot', help='path to be included. Can appear multiple times')
parser.add_argument('--pkgGroup', default='migration', help='package group')
parser.add_argument('--outZip', help='path to package zip file')
args = parser.parse_args()

aem = pyaem.pyaem.PyAem('admin', 'admin', 'localhost', 4502)

try:
    if aem.is_package_uploaded('mygroup', 'mypackage', '1.2.3'):
        aem.delete_package('mygroup', 'mypackage', '1.2.3')

    aem.create_package('mygroup', 'mypackage', '1.2.3')
    aem.update_package('mygroup', 'mypackage', '1.2.3', filter='[{"root":"/conf/magnum/sling:configs","rules":[]}]')
    aem.build_package('mygroup', 'mypackage', '1.2.3')

    aem.download_package('mygroup', 'mypackage', '1.2.3', '.')

    aem.upload_package('mypackage', '1.2.3', '.', force='true')

except PyAemException as e:
    # exception message
    print(e.message)

    # exception code uses response http_code
    print(e.code)

    # debug response and request details via exception
    print(e.response['http_code'])
    print(e.response['body'])
    print(e.response['request']['method'])
    print(e.response['request']['url'])
    print(e.response['request']['params'])

# create a tmp directory

# setup a package folder structure

# create a filter.xml file

# create a property file

# zip up to a zip file

# upload to AC with curl command

# build the package

# download the package
