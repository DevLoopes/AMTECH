"""Camada de acesso a arquivos TXT/JSON.

Fornece leitura/escrita atômica e lock por arquivo.
"""

import json
import os
import time
from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile


class FileDB:
    def __init__(self, data_dir: Path, lock_timeout: int = 5, lock_stale: int = 20):
        self.data_dir = Path(data_dir)
        self.lock_timeout = lock_timeout
        self.lock_stale = lock_stale

    def ensure_dirs(self):
        for p in [
            "users",
            "rooms",
            "sectors",
            "bookings",
            "requests",
            "notifications",
            "blocks",
            "logs",
            "_meta",
            "_backup",
        ]:
            (self.data_dir / p).mkdir(parents=True, exist_ok=True)

    @contextmanager
    def file_lock(self, target: Path):
        lock_file = target.with_suffix(target.suffix + ".lock")
        deadline = time.time() + self.lock_timeout
        while True:
            try:
                fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(time.time()).encode("utf-8"))
                os.close(fd)
                break
            except FileExistsError:
                try:
                    mtime = lock_file.stat().st_mtime
                    if (time.time() - mtime) > self.lock_stale:
                        lock_file.unlink(missing_ok=True)
                        continue
                except FileNotFoundError:
                    continue
                if time.time() >= deadline:
                    raise TimeoutError(f"lock timeout on {target}")
                time.sleep(0.05)
        try:
            yield
        finally:
            lock_file.unlink(missing_ok=True)

    def read_json(self, path: Path, default):
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            return default
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read().strip()
            if not raw:
                return default
            return json.loads(raw)

    def _write_atomic_unlocked(self, path: Path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile("w", delete=False, dir=path.parent, encoding="utf-8") as tf:
            json.dump(data, tf, ensure_ascii=False, indent=2)
            tf.flush()
            os.fsync(tf.fileno())
            tmp_name = tf.name
        os.replace(tmp_name, path)

    def write_json_atomic(self, path: Path, data, use_lock: bool = True):
        path.parent.mkdir(parents=True, exist_ok=True)
        if use_lock:
            with self.file_lock(path):
                self._write_atomic_unlocked(path, data)
        else:
            self._write_atomic_unlocked(path, data)
