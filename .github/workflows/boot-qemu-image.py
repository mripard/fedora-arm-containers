#!/usr/bin/env python3

# Based on https://git.buildroot.org/buildroot/tree/support/scripts/boot-qemu-image.py?h=2024.11-rc1
# This script expect to run from the top directory.

import os
import pexpect
import sys
import time

def main():
    if not (len(sys.argv) == 3):
        print("Error: incorrect number of arguments")
        print("""Usage: boot-qemu-image.py <path/to/start-qemu.sh> <path/to/container-image.raw>""")
        sys.exit(1)

    qemu_start = sys.argv[1]
    if not os.path.exists(qemu_start):
        print('start_qemu.sh is missing, cannot test.')
        sys.exit(0)

    image = sys.argv[2]
    child = pexpect.spawn(qemu_start, [image],
                          timeout=50, encoding='utf-8',
                          env={"QEMU_AUDIO_DRV": "none"})

    # We want only stdout into the log to avoid double echo
    child.logfile = sys.stdout

    # Let the spawn actually try to fork+exec to the wrapper, and then
    # let the wrapper exec the qemu process.
    time.sleep(1)

    try:
        child.expect(["systemd\[\d\]: Detected first boot."], timeout=300)
    except pexpect.EOF as e:
        # Some emulations require a fork of qemu-system, which may be
        # missing on the system, and is not provided by Buildroot.
        # In this case, spawn above will succeed at starting the wrapper
        # start-qemu.sh, but that one will fail (exit with 127) in such
        # a situation.
        exit = [int(line.split(' ')[1])
                for line in e.value.splitlines()
                if line.startswith('exitstatus: ')]
        if len(exit) and exit[0] == 127:
            print('qemu-start.sh could not find the qemu binary')
            sys.exit(0)
        print("Connection problem, exiting.")
        sys.exit(1)
    except pexpect.TIMEOUT:
        print("System did not boot in time, exiting.")
        sys.exit(1)

    try:
        child.expect(["Please enter user name to create (empty to skip):"], timeout=300)
    except pexpect.EOF as e:
        print("Cannot connect to shell.")
        sys.exit(1)
    except pexpect.TIMEOUT:
        print("System did not boot in time, exiting.")
        sys.exit(1)

    child.sendline("")

    try:
        child.expect(["[0-9a-f]{12} login:"], timeout=300)
    except pexpect.EOF as e:
        print("Cannot connect to shell.")
        sys.exit(1)
    except pexpect.TIMEOUT:
        print("System did not boot in time, exiting.")
        sys.exit(1)

    child.sendline("root\r")

    try:
        child.expect(["\\[root@[0-9a-f]{12} ~\\]# "], timeout=60)
    except pexpect.EOF:
        print("Cannot connect to shell")
        sys.exit(1)
    except pexpect.TIMEOUT:
        print("Timeout while waiting for shell")
        sys.exit(1)

    child.sendline("poweroff\r")

    try:
        child.expect(["System halted"], timeout=600)
        child.expect(pexpect.EOF)
    except pexpect.EOF:
        pass
    except pexpect.TIMEOUT:
        # Qemu may not exit properly after "System halted", ignore.
        print("Cannot halt machine")

    sys.exit(0)


if __name__ == "__main__":
    main()
