import subprocess


def test_cli():
    subprocess.check_call("poetry run python covid19count.py --help".split(" "))
