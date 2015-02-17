"""Operating system utilities.  Running commands, printing to stderr etc."""

from __future__ import print_function
import sys
import subprocess


def print_stderr(*objs):
    """Print to standard error."""
    print("", *objs, file=sys.stderr)


def getStdoutFromCmd(command, shell=False, stderr=False):
    """Execute command and capture stderr or stdout."""
    if stderr:
        child = subprocess.Popen(
            command, shell=shell, stderr=subprocess.PIPE, stdout=None)
    else:
        child = subprocess.Popen(
            command, shell=shell, stdout=subprocess.PIPE, stderr=None)

    output = ''

    while True:
        if stderr:
            out = child.stderr.read(1)
        else:
            out = child.stdout.read(1)

        if out == '' and child.poll() != None:
            break

        elif out != '':
            output += out

    return output


def getExitStatusFromCmd(command, shell=False, stderr=False):
    """Execute command and capture exit status."""
    if stderr:
        child = subprocess.Popen(
            command, shell=shell, stderr=subprocess.PIPE, stdout=None)
    else:
        child = subprocess.Popen(
            command, shell=shell, stdout=subprocess.PIPE, stderr=None)

    while True:
        poll = child.poll()
        if poll is not None:
            return poll
