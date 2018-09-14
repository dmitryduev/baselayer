#!/usr/bin/env python
from status import status

import os
import sys
import subprocess
import textwrap
from distutils.version import LooseVersion as Version


def output(cmd):
    p = subprocess.Popen(cmd,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = p.communicate()
    success = (p.returncode == 0)
    return success, out


deps = {
    'nginx': (
        # Command to get version
        ['nginx', '-v'],
        # Extract *only* the version number
        lambda v: v.split()[2].split('/')[1],
        # It must be >= 1.7
        '1.7'
    ),
    'supervisord': (
        ['supervisord', '-v'],
        lambda v: v,
        '3.0b2'
    ),
    'psql': (
        ['psql', '--version'],
        lambda v: v.split()[2],
        '10.5',
    ),
    'node (npm)': (
        ['npm', '-v'],
        lambda v: v,
        '5.8.0')
}

print('Checking system dependencies:')

fail = []

for dep, (cmd, get_version, min_version) in deps.items():
    try:
        with status(f'{dep} >= {min_version}'):
            success, out = output(cmd)
            try:
                version = get_version(out.decode('utf-8').strip())
            except:
                raise ValueError('Could not parse version')

            if not (Version(version) >= Version(min_version)):
                raise RuntimeError('Incorrect version')
    except ValueError:
        print(f'\n[!] Sorry, but our script could not parse the output of '
              f'`{" ".join(cmd)}`; please file a bug, or see '
              f'`check_app_environment.py`\n'
        )
        raise
    except:
        fail.append(dep)

if fail:
    print()
    print('[!] Some system dependencies seem to be unsatisfied')
    print()
    print('    The failed checks were:')
    print()
    for pkg in fail:
        cmd, get_version, min_version = deps[pkg]
        print(f'    - {pkg}: `{" ".join(cmd)}` should indicate version >= '
              f'{min_version}')
    print()
    print('    Please refer to https://cesium-ml.org/baselayer')
    print('      for installation instructions.')
    print()
    sys.exit(-1)

print()
try:
    with status('Baselayer installed inside of app'):
        if not (os.path.exists('../config.yaml') or
                os.path.exists('../config.yaml.defaults')):
            raise RuntimeError()
except:
    print(textwrap.dedent('''
          It does not look as though baselayer is deployed as
          part of an application.

          Please see

            https://github.com/cesium-ml/baselayer_template_app

          for an example application.
    '''))
    sys.exit(-1)

print('-' * 20)
