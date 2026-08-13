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
    # Rendering the diagnostic must never replace the closed stdout result with
    # another crash: third-party exceptions can have a broken __str__, and
    # stderr can disappear while handling the original failure.
    try:
        try:
            detail = str(exc)
        except BaseException:
            detail = "<unprintable exception>"
        text = f"{type(exc).__name__}: {detail}".encode(
            "utf-8",
            errors="replace",
        )[:MAX_OPERATOR_DETAIL_BYTES]
    except BaseException:
        text = b"unprintable classifier exception"
    try:
        sys.stderr.buffer.write(text)
        sys.stderr.buffer.flush()
    except BaseException:
        pass


def _normalize_result(classified: Any) -> dict[str, Any]:
    try:
        raw_pdf_type = classified.pdf_type
        raw_confidence = classified.confidence
        raw_pages = classified.pages_needing_ocr
    except BaseException as exc:
        _operator_detail(exc)
        return _unavailable("INVALID_CLASSIFIER_RESULT")

    if type(raw_pdf_type) is not str or not raw_pdf_type:
        return _unavailable("INVALID_CLASSIFIER_RESULT")
    if type(raw_confidence) not in (int, float):
        return _unavailable("INVALID_CLASSIFIER_RESULT")
    try:
        confidence = float(raw_confidence)
    except BaseException as exc:
        _operator_detail(exc)
        return _unavailable("INVALID_CLASSIFIER_RESULT")
    if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
        return _unavailable("INVALID_CLASSIFIER_RESULT")

    try:
        iterator = iter(raw_pages)
    except BaseException as exc:
        _operator_detail(exc)
        return _unavailable("INVALID_CLASSIFIER_RESULT")

    pages: list[int] = []
    seen: set[int] = set()
    try:
        for page in iterator:
            if len(pages) >= MAX_PAGE_ENTRIES:
                return _unavailable("INVALID_CLASSIFIER_RESULT")
            if type(page) is not int or page < 0:
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
        "confidence": confidence,
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

    try:
        normalized = _normalize_result(classified)
    except BaseException as exc:
        # Final adapter backstop: a future normalization branch must not let a
        # malformed third-party object escape the closed stdout contract.
        _operator_detail(exc)
        normalized = _unavailable("INVALID_CLASSIFIER_RESULT")
    _emit(normalized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
