"""
Tests for landsync_datasets Command-Line Interface.
"""

import pytest
from landsync_datasets.cli import main


def test_cli_validate_command():
    ret = main(["validate", "--path", "datasets/landsync-india-synthetic"])
    assert ret == 0


def test_cli_report_command():
    ret = main(["report", "--path", "datasets/landsync-india-synthetic"])
    assert ret == 0
