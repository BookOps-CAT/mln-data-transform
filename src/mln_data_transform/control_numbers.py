from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ControlNumberGenerator:
    def __init__(self, state_file: str | None = None, start: int = 1):
        self.state_path = Path(state_file)
        self.used_numbers = set()
        self.next_number = start

        if state_file is not None:
            self._load_state()

    def _load_state(self):
        if not self.state_path.exists():
            return
        data = json.loads(self.state_path.read_text())
        logger.info(data)
        self.used_numbers = set(data.get("used_numbers", []))
        if self.used_numbers:
            self.next_number = max(self.used_numbers) + 1

    def _format(self, number: int) -> str:
        return f"nn-mlnyc-{number:07d}"

    def next_control_number(self) -> str:
        while self.next_number in self.used_numbers:
            self.next_number += 1
        number = self.next_number
        self.used_numbers.add(number)
        self.next_number += 1
        return self._format(number)

    def save_state(self):
        self.state_path.write_text(
            json.dumps({"used_numbers": sorted(self.used_numbers)})
        )
