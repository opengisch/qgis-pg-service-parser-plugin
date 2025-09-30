import stat
from pathlib import Path
from typing import Optional

try:
    import pgserviceparser
except ModuleNotFoundError:
    from pg_service_parser.libs import pgserviceparser


def __make_file_writable(path: Path):
    current_permission = stat.S_IMODE(path.stat().st_mode)
    WRITE = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
    path.chmod(current_permission | WRITE)  # May trigger permission error


def __whenReadOnlyTryToAddWritePermission(func):
    """
    Decorator to be applied to functions that attempt to modify a service file.

    If the file is read-only, a PermissionError exception will be raised by the
    underlying lib.

    This decorator handles that error by attempting to set write permissions
    (which works if the user is the owner of that file or has proper rights to
    alter the file permissions, e.g., because it's inheriting them from the
    parent), and rerunning the decorated function with the newly writable file.

    However, if the user is not the file owner (or cannot modify permissions on
    the file), permissions won't be set, and we'll raise the PermissionError so
    that it can be handled by the GUI.
    """

    def wrapper(*args, **kwargs):
        attempt = 0  # After eventual fail, we'll attempt only once more
        while attempt <= 1:
            try:
                return func(*args, **kwargs)
            except PermissionError:
                if attempt == 1:  # If it's the 2nd attempt, leave with error
                    raise

                try:
                    __make_file_writable(conf_path())
                except PermissionError:
                    pass  # Ignore PermissionError by chmod()
                finally:
                    attempt += 1

    return wrapper


def conf_path(create_if_missing: Optional[bool] = False) -> Path:
    return pgserviceparser.conf_path(create_if_missing)


def service_names(conf_file_path: Optional[Path] = None, sorted_alphabetically=False) -> list[str]:
    res = pgserviceparser.service_names(conf_file_path)
    return sorted(res, key=str.lower) if sorted_alphabetically else res


@__whenReadOnlyTryToAddWritePermission
def add_new_service(service_name: str, conf_file_path: Optional[Path] = None) -> bool:
    return create_service(service_name, {}, conf_file_path)


def service_config(service_name: str, conf_file_path: Optional[Path] = None) -> dict:
    return pgserviceparser.service_config(service_name, conf_file_path)


@__whenReadOnlyTryToAddWritePermission
def write_service(
    service_name: str,
    settings: dict,
    conf_file_path: Optional[Path] = None,
):
    pgserviceparser.write_service(service_name, settings, conf_file_path)


def write_service_to_text(service_name: str, settings: dict) -> str:
    return pgserviceparser.write_service_to_text(service_name, settings)


def create_service(
    service_name: str, settings: dict, conf_file_path: Optional[Path] = None
) -> bool:
    config = pgserviceparser.full_config(conf_file_path)
    if service_name in config:
        return False

    config.add_section(service_name)
    with open(conf_file_path or pgserviceparser.conf_path(), "w") as f:
        config.write(f, space_around_delimiters=False)

    if service_name in config:
        pgserviceparser.write_service(service_name, settings, conf_file_path)
        return True

    return False


@__whenReadOnlyTryToAddWritePermission
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
