#!/usr/bin/env python3
"""ASF Infra App uninstaller"""
import sys
import os
import subprocess
import typing

programs_to_remove = ["kif", "loggy", "blocky"]

debug_mode = len(sys.argv) == 2 and sys.argv[1] == "debug"
systemctl = "/bin/systemctl"
default_install_dir = "/usr/local/etc"

systemd_paths = [
    "/etc/systemd/system/",
    "/usr/lib/systemd/system/",
    "/lib/systemd/system/",
    "/etc/init.d/",
]


def find_systemd_files(svcname: str) -> typing.List[str]:
    """Finds all systemd/upstart files pertaining to a service and returns as a list"""
    found_files = []
    for path in systemd_paths:
        upath = os.path.join(path, svcname)
        dpath = os.path.join(path, svcname + ".service")
        if os.path.exists(upath):
            found_files.append(upath)
        if os.path.exists(dpath):
            found_files.append(dpath)
    return found_files


def print_line(txt: str):
    sys.stdout.write("%-64s" % txt)
    sys.stdout.flush()


def uninstall_service(svcname: str):
    """Uninstalls a service"""
    print("-" * 64)
    print("Uninstalling application %s..." % svcname)
    print("-" * 64)
    print_line("Stopping systemd service %s." % svcname)
    if not debug_mode:
        subprocess.check_call((systemctl, "stop", svcname))
    print("[DONE]")

    print_line("Disabling systemd service %s." % svcname)
    if not debug_mode:
        subprocess.check_call((systemctl, "disable", svcname))
    print("[DONE]")

    for filepath in find_systemd_files(svcname):
        print_line("Removing init file %s" % filepath)
        if not debug_mode:
            os.unlink(filepath)
        print("[DONE]")

    print_line("Reloading systemd modules")
    if not debug_mode:
        subprocess.check_call((systemctl, "daemon-reload"))
    print("[DONE]")

    print_line("Resetting failed systemd paths")
    if not debug_mode:
        subprocess.check_call((systemctl, "reset-failed"))
    print("[DONE]")

    print("Removing application files")
    installroot = os.path.join(default_install_dir, svcname)
    if os.path.isdir(installroot):
        print("Entering %s" % installroot)
        for file in os.listdir(installroot):
            fpath = os.path.join(installroot, file)
            print_line("Removing %s" % fpath)
            if not debug_mode:
                os.unlink(fpath)
            print("[DONE]")
        print_line("Removing parent install dir %s" % installroot)
        if not debug_mode:
            os.rmdir(installroot)
        print("[DONE]")
    print("Service %s has been fully removed!" % svcname)
    print("-" * 64)


def main():
    if debug_mode:
        print("Debug mode enabled, not removing applications, just pretending.")
    for program in programs_to_remove:
        try:
            subprocess.check_output(
                (systemctl, "--no-pager", "status", program), stderr=subprocess.PIPE
            )
            has_service = True
        except subprocess.CalledProcessError as e:
            if e.returncode == 4:  # No such service
                has_service = False
            else:
                has_service = True
        if has_service:
            print("- %s is installed as systemd service, removing" % program)
            uninstall_service(program)
        else:
            print("- %s is not installed as systemd service" % program)


if __name__ == "__main__":
    main()
