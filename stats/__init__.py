from pathlib import Path
from json import load, dump
from re import A


class UploadedItem(dict[str, int]):
    """Statistics on a singular upload. A mapping of username to total times uploaded."""

    def sum(self) -> int:
        return sum(self.values())


class UploadedItems(dict[str, UploadedItem]):
    """Statistics on all uploads. A mapping of upload name to UploadedItem."""

    def sums(self) -> dict[str, int]:
        return {k: v.sum() for k, v in self.items()}

    def __init__(self, path: Path, **mapping: UploadedItem):
        super().__init__(mapping)
        self.path = path.resolve()

    @classmethod
    def from_path(cls, path: Path) -> "UploadedItems":
        with open(path, "r", encoding="utf-8") as file:
            res = load(file)
        return cls(path, **{k: UploadedItem(v) for k, v in res.items()})

    def to_path(self, path: Path | None = None):
        path = path.resolve() if path else self.path

        # if an earlier save is found, back it up
        if path.exists():
            from datetime import datetime

            name = path.name.removesuffix(path.suffix)
            now = int(datetime.utcnow().timestamp())
            path.rename(path.parent / f"{name}.{now}{path.suffix}")

        with open(path, "w", encoding="utf-8") as file:
            dump(self, file)
