import pytest

from molecule import config
from molecule_driver_libvirt import driver

def test_libvirt_name_property():
    instance = driver.Libvirt(None)
    assert instance.name == "molecule_libvirt"
