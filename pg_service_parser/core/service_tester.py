from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

from qgis.core import QgsTask
from qgis.PyQt.QtCore import QCoreApplication, pyqtSignal

try:
    import psycopg
except ImportError:
    try:
        import psycopg2 as psycopg
    except ImportError:
        psycopg = None

CONNECT_TIMEOUT = 10  # seconds
MAX_PARALLEL_CONNECTIONS = 8


def psycopg_available() -> bool:
    return psycopg is not None


def connection_error(params: dict) -> str | None:
    """Connects with the given parameters and returns the error message, or None on success."""
    try:
        psycopg.connect(**{**params, "connect_timeout": CONNECT_TIMEOUT}).close()
    except Exception as e:
        return str(e).strip() or type(e).__name__
    return None


class ServiceTesterTask(QgsTask):
    """Tests the connection to PG services, several at a time."""

    service_tested = pyqtSignal(str, str)  # service name, error message (empty on success)

    def __init__(self, services: dict[str, dict]):
        """Services are given as connection parameters by service name."""
        super().__init__(QCoreApplication.translate("ServiceTesterTask", "Testing PG services"))
        self.__services = services

    def run(self) -> bool:
        executor = ThreadPoolExecutor(max_workers=MAX_PARALLEL_CONNECTIONS)
        futures = {
            executor.submit(connection_error, params): name
            for name, params in self.__services.items()
        }
        pending = set(futures)
        while pending:
            if self.isCanceled():
                # Connections in progress are left to time out on their own
                executor.shutdown(wait=False, cancel_futures=True)
                return False

            done, pending = wait(pending, timeout=0.2, return_when=FIRST_COMPLETED)
            for future in done:
                self.service_tested.emit(futures[future], future.result() or "")
            self.setProgress(100 * (len(futures) - len(pending)) / len(futures))

        executor.shutdown()
        return True
