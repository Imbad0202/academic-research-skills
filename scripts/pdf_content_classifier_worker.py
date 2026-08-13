"""Isolated optional PDF content-classifier worker.

This process is the only place that imports or invokes ``pdf_inspector``.  It
receives the exact bytes already hashed by ``pdf_read_preflight.py`` on stdin
and emits one small, closed JSON object on stdout.  Any native panic, abort, or
segmentation fault is therefore contained to this child and interpreted by the
parent as an unavailable advisory signal.

The worker deliberately never emits the upstream classifier's free-form
``pdf_type`` or exception text on stdout.  Bounded exception detail is written
only to stderr, which the parent discards unless the operator explicitly asks
for a separate local diagnostic file.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import math
import sys
from typing import Any

SCHEMA = "pdf_content_classifier_worker/1"
MAX_PAGE_ENTRIES = 50_000
MAX_OPERATOR_DETAIL_BYTES = 512


def _emit(payload: dict[str, Any]) -> None:
    raw = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    sys.stdout.buffer.write(raw + b"\n")
    sys.stdout.buffer.flush()


def _unavailable(reason: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "status": "UNAVAILABLE",
        "reason": reason,
        "classification": None,
        "confidence": None,
        "pages_needing_ocr": None,
    }


def _operator_detail(exc: BaseException) -> None:
    # This stream is never copied into the prompt-facing sidecar.  Bound bytes
    # before writing so even a hostile exception string cannot flood the pipe.
    text = f"{type(exc).__name__}: {exc}".encode("utf-8", errors="replace")
    sys.stderr.buffer.write(text[:MAX_OPERATOR_DETAIL_BYTES])
    sys.stderr.buffer.flush()


def _normalize_result(classified: Any) -> dict[str, Any]:
    try:
        raw_pdf_type = classified.pdf_type
        raw_confidence = classified.confidence
        raw_pages = classified.pages_needing_ocr
    except BaseException as exc:
        _operator_detail(exc)
        return _unavailable("INVALID_CLASSIFIER_RESULT")

    if not isinstance(raw_pdf_type, str) or not raw_pdf_type:
        return _unavailable("INVALID_CLASSIFIER_RESULT")
    if (
        isinstance(raw_confidence, bool)
        or not isinstance(raw_confidence, (int, float))
        or not math.isfinite(float(raw_confidence))
        or not 0.0 <= float(raw_confidence) <= 1.0
    ):
        return _unavailable("INVALID_CLASSIFIER_RESULT")

    try:
        iterator = iter(raw_pages)
    except TypeError:
        return _unavailable("INVALID_CLASSIFIER_RESULT")

    pages: list[int] = []
    seen: set[int] = set()
    try:
        for page in iterator:
            if len(pages) >= MAX_PAGE_ENTRIES:
                return _unavailable("INVALID_CLASSIFIER_RESULT")
            if isinstance(page, bool) or not isinstance(page, int) or page < 0:
                return _unavailable("INVALID_CLASSIFIER_RESULT")
            if page in seen:
                return _unavailable("INVALID_CLASSIFIER_RESULT")
            seen.add(page)
            pages.append(page)
    except BaseException as exc:
        _operator_detail(exc)
        return _unavailable("INVALID_CLASSIFIER_RESULT")

    pages.sort()
    # Do not expose an open upstream enum.  The one positively recognized
    # state is text_based with no OCR pages; every other non-empty upstream
    # type is conservatively reduced to the closed OCR_RECOMMENDED advisory.
    classification = (
        "TEXT_AVAILABLE"
        if raw_pdf_type == "text_based" and not pages
        else "OCR_RECOMMENDED"
    )
    return {
        "schema": SCHEMA,
        "status": "CLASSIFIED",
        "reason": "CLASSIFIED",
        "classification": classification,
        "confidence": float(raw_confidence),
        "pages_needing_ocr": pages,
    }


def main() -> int:
    try:
        pdf_inspector_spec = importlib.util.find_spec("pdf_inspector")
    except BaseException as exc:
        _operator_detail(exc)
        _emit(_unavailable("CLASSIFIER_ERROR"))
        return 0
    if pdf_inspector_spec is None:
        _emit(_unavailable("DEPENDENCY_ABSENT"))
        return 0

    try:
        pdf_inspector = importlib.import_module("pdf_inspector")
    except BaseException as exc:
        _operator_detail(exc)
        _emit(_unavailable("CLASSIFIER_ERROR"))
        return 0

    try:
        data = sys.stdin.buffer.read()
        classified = pdf_inspector.classify_pdf_bytes(data)
    except BaseException as exc:
        _operator_detail(exc)
        _emit(_unavailable("CLASSIFIER_ERROR"))
        return 0

    _emit(_normalize_result(classified))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
