"""Bounded, traversal-safe extraction for untrusted Office ZIP containers."""

from __future__ import annotations

import os
import stat
import unicodedata
import zipfile
from pathlib import Path, PurePosixPath

_MAX_ENTRIES = 10_000
_MAX_MEMBER_BYTES = 256 * 1024 * 1024
_MAX_TOTAL_BYTES = 512 * 1024 * 1024
_MAX_COMPRESSION_RATIO = 1_000
_CHUNK_BYTES = 1024 * 1024
_WINDOWS_RESERVED_STEMS = frozenset(
    {"aux", "clock$", "con", "conin$", "conout$", "nul", "prn"}
    | {f"com{index}" for index in range(1, 10)}
    | {f"lpt{index}" for index in range(1, 10)}
    | {f"com{index}" for index in "¹²³"}
    | {f"lpt{index}" for index in "¹²³"}
)
_WINDOWS_FORBIDDEN_CHARS = frozenset('<>"|?*')


class UnsafeArchiveError(ValueError):
    """Raised when an archive violates the document-tool extraction boundary."""


def _windows_key(parts: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(unicodedata.normalize("NFC", part).casefold() for part in parts)


def _member_parts(info: zipfile.ZipInfo) -> tuple[str, ...]:
    original_name = getattr(info, "orig_filename", info.filename)
    if not isinstance(original_name, str):
        raise UnsafeArchiveError("archive member path was rejected")
    name = original_name.replace("\\", "/")
    try:
        encoded_name = name.encode("utf-8")
    except UnicodeError as exc:
        raise UnsafeArchiveError("archive member path was rejected") from exc
    if (
        not name
        or "\x00" in name
        or name.startswith("/")
        or ":" in name
        or len(encoded_name) > 4_096
    ):
        raise UnsafeArchiveError("archive member path was rejected")
    normalized_name = name[:-1] if name.endswith("/") else name
    raw_parts = normalized_name.split("/")
    parts = PurePosixPath(normalized_name).parts
    if (
        not normalized_name
        or not parts
        or len(parts) > 256
        or tuple(raw_parts) != parts
        or any(part in {"", ".", ".."} for part in raw_parts)
    ):
        raise UnsafeArchiveError("archive member path was rejected")
    for part in parts:
        try:
            encoded_part = part.encode("utf-8")
        except UnicodeError as exc:
            raise UnsafeArchiveError("archive member path was rejected") from exc
        stem = part.split(".", 1)[0].rstrip(" .").casefold()
        if (
            len(part) > 255
            or len(encoded_part) > 255
            or part.endswith((" ", "."))
            or stem in _WINDOWS_RESERVED_STEMS
            or any(ord(character) < 32 for character in part)
            or any(character in _WINDOWS_FORBIDDEN_CHARS for character in part)
        ):
            raise UnsafeArchiveError("archive member path was rejected")

    unix_mode = (info.external_attr >> 16) & 0xFFFF
    member_type = stat.S_IFMT(unix_mode)
    if member_type not in {0, stat.S_IFDIR, stat.S_IFREG}:
        raise UnsafeArchiveError("archive special member was rejected")
    path_is_directory = name.endswith("/")
    if (member_type == stat.S_IFDIR) != path_is_directory and member_type:
        raise UnsafeArchiveError("archive member type was rejected")
    if info.flag_bits & 0x1:
        raise UnsafeArchiveError("encrypted archive members are unsupported")
    if info.file_size < 0 or info.compress_size < 0:
        raise UnsafeArchiveError("archive member size was rejected")
    if info.file_size > _MAX_MEMBER_BYTES:
        raise UnsafeArchiveError("archive member exceeds the size boundary")
    if info.file_size and (
        info.compress_size == 0
        or info.file_size > _MAX_COMPRESSION_RATIO * info.compress_size
    ):
        raise UnsafeArchiveError("archive member exceeds the compression boundary")
    return parts


def _is_link_like(path: Path) -> bool:
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return False
    except OSError:
        return True
    if stat.S_ISLNK(metadata.st_mode):
        return True
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    file_attributes = getattr(metadata, "st_file_attributes", 0)
    if reparse_flag and file_attributes & reparse_flag:
        return True
    is_junction = getattr(path, "is_junction", None)
    try:
        return bool(callable(is_junction) and is_junction())
    except OSError:
        return True


def _private_directory(
    root: Path,
    parts: tuple[str, ...],
    created_directories: list[Path],
) -> Path:
    current = root
    for part in parts:
        candidate = current / part
        if _is_link_like(candidate):
            raise UnsafeArchiveError("archive destination contains a symlink")
        if candidate.exists():
            if not candidate.is_dir():
                raise UnsafeArchiveError("archive destination type conflicts")
        else:
            try:
                candidate.mkdir(mode=0o700)
                created_directories.append(candidate)
            except FileExistsError:
                if _is_link_like(candidate) or not candidate.is_dir():
                    raise UnsafeArchiveError(
                        "archive destination type conflicts"
                    ) from None
        try:
            candidate.resolve(strict=True).relative_to(root)
        except (OSError, ValueError) as exc:
            raise UnsafeArchiveError("archive destination escaped its root") from exc
        current = candidate
    return current


def _validated_members(
    archive: zipfile.ZipFile,
    *,
    max_entries: int,
    max_total_bytes: int,
) -> list[tuple[zipfile.ZipInfo, tuple[str, ...], bool]]:
    if (
        isinstance(max_entries, bool)
        or not isinstance(max_entries, int)
        or not 1 <= max_entries <= _MAX_ENTRIES
        or isinstance(max_total_bytes, bool)
        or not isinstance(max_total_bytes, int)
        or not 1 <= max_total_bytes <= _MAX_TOTAL_BYTES
    ):
        raise UnsafeArchiveError("archive extraction limits were rejected")
    infos = archive.infolist()
    if len(infos) > max_entries:
        raise UnsafeArchiveError("archive contains too many members")

    members: list[tuple[zipfile.ZipInfo, tuple[str, ...], bool]] = []
    seen: set[tuple[str, ...]] = set()
    file_keys: set[tuple[str, ...]] = set()
    directory_keys: set[tuple[str, ...]] = set()
    declared_total = 0
    for info in infos:
        parts = _member_parts(info)
        is_directory = info.is_dir() or info.filename.endswith(("/", "\\"))
        key = _windows_key(parts)
        if key in seen:
            raise UnsafeArchiveError("archive contains colliding member paths")
        seen.add(key)
        declared_total += info.file_size
        if declared_total > max_total_bytes:
            raise UnsafeArchiveError("archive exceeds the total size boundary")
        if is_directory:
            directory_keys.add(key)
        else:
            file_keys.add(key)
        members.append((info, parts, is_directory))

    if file_keys & directory_keys:
        raise UnsafeArchiveError("archive member types conflict")
    for key in file_keys:
        if any(key[:index] in file_keys for index in range(1, len(key))):
            raise UnsafeArchiveError("archive member types conflict")
    return members


def safe_extract_zip(
    archive: zipfile.ZipFile,
    destination: str | os.PathLike[str],
    *,
    max_entries: int = _MAX_ENTRIES,
    max_total_bytes: int = _MAX_TOTAL_BYTES,
) -> None:
    """Extract a ZIP without traversal, links, special files, or unbounded expansion."""

    members = _validated_members(
        archive,
        max_entries=max_entries,
        max_total_bytes=max_total_bytes,
    )

    root = Path(destination)
    if _is_link_like(root):
        raise UnsafeArchiveError("archive destination was rejected")
    try:
        root.mkdir(mode=0o700, parents=True, exist_ok=True)
        if _is_link_like(root) or not root.is_dir():
            raise UnsafeArchiveError("archive destination was rejected")
        root = root.resolve(strict=True)
    except UnsafeArchiveError:
        raise
    except OSError as exc:
        raise UnsafeArchiveError("archive destination was rejected") from exc

    written_total = 0
    created_files: list[Path] = []
    created_directories: list[Path] = []
    completed = False
    try:
        for info, parts, is_directory in members:
            if is_directory:
                _private_directory(root, parts, created_directories)
                continue

            parent = _private_directory(root, parts[:-1], created_directories)
            target = parent / parts[-1]
            if _is_link_like(target) or target.exists():
                raise UnsafeArchiveError("archive destination type conflicts")

            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            if hasattr(os, "O_BINARY"):
                flags |= os.O_BINARY
            if hasattr(os, "O_CLOEXEC"):
                flags |= os.O_CLOEXEC
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            try:
                descriptor = os.open(target, flags, 0o600)
            except OSError as exc:
                raise UnsafeArchiveError(
                    "archive destination type conflicts"
                ) from exc
            created_files.append(target)
            member_written = 0
            try:
                with archive.open(info, "r") as source, os.fdopen(
                    descriptor, "wb", closefd=True
                ) as output:
                    descriptor = -1
                    while True:
                        chunk = source.read(_CHUNK_BYTES)
                        if not chunk:
                            break
                        member_written += len(chunk)
                        written_total += len(chunk)
                        if (
                            member_written > info.file_size
                            or member_written > _MAX_MEMBER_BYTES
                            or written_total > max_total_bytes
                        ):
                            raise UnsafeArchiveError(
                                "archive expansion exceeds the size boundary"
                            )
                        output.write(chunk)
                if member_written != info.file_size:
                    raise UnsafeArchiveError(
                        "archive member size did not match metadata"
                    )
            finally:
                if descriptor >= 0:
                    os.close(descriptor)
        completed = True
    finally:
        if not completed:
            for path in reversed(created_files):
                try:
                    path.unlink(missing_ok=True)
                except OSError:
                    pass
            for path in reversed(created_directories):
                try:
                    path.rmdir()
                except OSError:
                    pass
