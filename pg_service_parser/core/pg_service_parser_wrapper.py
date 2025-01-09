from pathlib import Path
from typing import List, Optional

from pg_service_parser.libs import pgserviceparser


def conf_path(create_if_missing: Optional[bool] = False) -> Path:
    return pgserviceparser.conf_path(create_if_missing)


def service_names(conf_file_path: Optional[Path] = None) -> List[str]:
    return pgserviceparser.service_names(conf_file_path)


def add_new_service(service_name: str, conf_file_path: Optional[Path] = None) -> bool:
    return create_service(service_name, {}, conf_file_path)


def service_config(service_name: str, conf_file_path: Optional[Path] = None) -> dict:
    return pgserviceparser.service_config(service_name, conf_file_path)


def write_service(
    service_name: str,
    settings: dict,
    conf_file_path: Optional[Path] = None,
):
    pgserviceparser.write_service(service_name, settings, conf_file_path)


def create_service(
    service_name: str, settings: dict, conf_file_path: Optional[Path] = None
) -> bool:
    config = pgserviceparser.full_config(conf_file_path)
    if service_name in config:
        return False

    config.add_section(service_name)
    with open(conf_file_path or pgserviceparser.conf_path(), "w") as f:
        config.write(f)

    if service_name in config:
        pgserviceparser.write_service(service_name, settings, conf_file_path)
        return True

    return False


def copy_service_settings(
    source_service_name: str, target_service_name: str, conf_file_path: Optional[Path] = None
):
    settings = pgserviceparser.service_config(source_service_name, conf_file_path)
    config = pgserviceparser.full_config(conf_file_path)

    if target_service_name in config:
        pgserviceparser.write_service(target_service_name, settings, conf_file_path)
    else:
        create_service(target_service_name, settings, conf_file_path)


if __name__ == "__main__":
    assert service_names() == []

    # Add new service
    _settings = {
        "host": "localhost",
        "port": "5432",
        "user": "postgres",
        "password": "secret",
        "dbname": "qgis_test_db",
    }
    assert create_service("qgis-test", _settings)
    assert service_names() == ["qgis-test"]

    # Clone existing service
    copy_service_settings("qgis-test", "qgis-demo")
    assert service_names() == ["qgis-test", "qgis-demo"]
    assert service_config("qgis-demo") == _settings

    # Add new service
    _settings = {
        "host": "localhost",
        "port": "5433",
        "user": "admin",
        "password": "secret",
        "dbname": "qgis_test_db2",
    }
    assert create_service("qgis-new-test", _settings)
    assert service_names() == ["qgis-test", "qgis-demo", "qgis-new-test"]
    assert service_config("qgis-new-test") == _settings

    # Override existing qgis-test
    assert copy_service_settings("qgis-new-test", "qgis-test")
    assert service_names() == ["qgis-test", "qgis-demo", "qgis-new-test"]
    assert service_config("qgis-test") == _settings
