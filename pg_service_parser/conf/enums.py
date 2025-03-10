from enum import Enum


class SslModeEnum(Enum):
    DISABLE = "disable"
    ALLOW = "allow"
    PREFER = "prefer"
    REQUIRE = "require"
    VERIFY_CA = "verify-ca"
    VERIFY_FULL = "verify-full"


class WidgetTypeEnum(Enum):
    COMBOBOX = 0
    FILEWIDGET = 1
