"""Mutation tests for check_distribution_surface_claims.py (#753)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from check_distribution_surface_claims import run  # noqa: E402

CLEAN_PLUGIN = {
    "name": "fixture",
    "description": "Contract-audited academic research pipeline. "
                   "4 skills, 27 modes, 39 prompt roles.",
}
CLEAN_MARKETPLACE = {
    "name": "fixture",
    "description": "Contract-audited research and writing skills.",
    "plugins": [
        {"name": "fixture", "description": "4 skills + 27 modes."},
    ],
}


def _write(root: Path, plugin=CLEAN_PLUGIN, marketplace=CLEAN_MARKETPLACE,
           plugin_raw: str | None = None) -> Path:
    d = root / ".claude-plugin"
    d.mkdir(parents=True, exist_ok=True)
    if plugin is not None or plugin_raw is not None:
        (d / "plugin.json").write_text(
            plugin_raw if plugin_raw is not None else json.dumps(plugin),
            encoding="utf-8",
        )
    if marketplace is not None:
        (d / "marketplace.json").write_text(
            json.dumps(marketplace), encoding="utf-8"
        )
    return root


def _fires(errors: list[str], fragment: str) -> None:
    assert any(fragment in e for e in errors), (
        f"expected an error containing {fragment!r}, got: {errors}"
    )


def test_shipped_manifests_pass():
    assert run(REPO_ROOT) == []


def test_clean_synthetic_manifests_pass(tmp_path):
    assert run(_write(tmp_path)) == []


def test_missing_plugin_json_fails_closed(tmp_path):
    _write(tmp_path, plugin=None)
    _fires(run(tmp_path), "D1")


def test_missing_marketplace_json_fails_closed(tmp_path):
    _write(tmp_path, marketplace=None)
    _fires(run(tmp_path), "D1")


def test_unparseable_plugin_json_fails_closed(tmp_path):
    _write(tmp_path, plugin_raw="{not json", plugin=None)
    _fires(run(tmp_path), "D1")


def test_non_object_top_level_fails_closed(tmp_path):
    _write(tmp_path, plugin_raw='["a list"]', plugin=None)
    _fires(run(tmp_path), "D1")


def test_nonstandard_json_nan_fails_closed(tmp_path):
    # json.loads accepts NaN by default; strict consumers reject it
    _write(tmp_path, plugin=None,
           plugin_raw='{"description": "39 prompt roles", "score": NaN}')
    _fires(run(tmp_path), "D1")


def test_nonstandard_json_infinity_fails_closed(tmp_path):
    _write(tmp_path, plugin=None,
           plugin_raw='{"description": "39 prompt roles", "x": Infinity}')
    _fires(run(tmp_path), "D1")


def test_missing_description_fires_d2(tmp_path):
    _write(tmp_path, plugin={"name": "fixture"})
    _fires(run(tmp_path), "D2")


def test_empty_description_fires_d2(tmp_path):
    _write(tmp_path, plugin={"name": "fixture", "description": "   "})
    _fires(run(tmp_path), "D2")


def test_empty_plugins_list_fires_d2(tmp_path):
    _write(tmp_path, marketplace={"name": "f", "description": "ok",
                                  "plugins": []})
    _fires(run(tmp_path), "D2")


def test_production_grade_fires_d3(tmp_path):
    _write(tmp_path, plugin={
        "name": "f", "description": "Production-grade research pipeline."
    })
    _fires(run(tmp_path), "production-grade")


def test_production_grade_space_spelling_fires_d3(tmp_path):
    _write(tmp_path, plugin={
        "name": "f", "description": "A production grade pipeline."
    })
    _fires(run(tmp_path), "production-grade")


def test_agent_ensemble_fires_d3(tmp_path):
    _write(tmp_path, plugin={
        "name": "f", "description": "A 39-agent ensemble for research."
    })
    _fires(run(tmp_path), "agent ensemble")


def test_effectiveness_stems_fire_d3(tmp_path):
    for phrase in ("guaranteed accuracy", "proven results",
                   "state-of-the-art pipeline", "improves error rates",
                   "outperforms manual review"):
        errors = run(_write(tmp_path, plugin={
            "name": "f", "description": f"A pipeline with {phrase}."
        }))
        _fires(errors, "D3")


def test_provenance_does_not_false_fire(tmp_path):
    # word boundary: "proven" must not fire inside "provenance"
    assert run(_write(tmp_path, plugin={
        "name": "f",
        "description": "Citation provenance tracking — 39 prompt roles.",
    })) == []


def test_marketplace_plugin_entry_description_covered(tmp_path):
    _write(tmp_path, marketplace={
        "name": "f", "description": "ok",
        "plugins": [{"name": "f",
                     "description": "Production-grade skills."}],
    })
    _fires(run(tmp_path), "plugins[0]")


def test_percentage_figure_fires_d3(tmp_path):
    # the T-3 class: "31% -> ~5-10%" style numbers on a marketing surface
    _write(tmp_path, plugin={
        "name": "f",
        "description": "Cuts citation errors by 31% — 39 prompt roles.",
    })
    _fires(run(tmp_path), "percentage")


def test_missing_count_token_fires_d4(tmp_path):
    _write(tmp_path, plugin={
        "name": "f", "description": "Contract-audited research pipeline."
    })
    _fires(run(tmp_path), "D4")


def test_unbindable_count_spelling_fires_d4(tmp_path):
    # "39 agents" is a spelling invariant 8 cannot bind — the number would
    # silently detach from the tree count
    _write(tmp_path, plugin={
        "name": "f", "description": "A pipeline with 39 agents."
    })
    _fires(run(tmp_path), "D4")


def test_plugin_exposed_count_drift_fires_d5(tmp_path):
    _write(tmp_path, plugin={
        "name": "f",
        "description": "39 prompt roles (4 plugin-exposed agents).",
    })
    _fires(run(tmp_path), "D5")


def test_plugin_exposed_count_matching_passes(tmp_path):
    assert run(_write(tmp_path, plugin={
        "name": "f",
        "description": "39 prompt roles (3 plugin-exposed agents).",
    })) == []


def test_percentage_case_variant_fires_d3(tmp_path):
    # "_PERCENT_RE" is lowercase-only; the caller must lowercase first
    _write(tmp_path, plugin={
        "name": "f",
        "description": "A 31 Percent reduction — 39 prompt roles.",
    })
    _fires(run(tmp_path), "percentage")


def test_plugin_exposed_case_variant_fires_d5(tmp_path):
    _write(tmp_path, plugin={
        "name": "f",
        "description": "39 prompt roles (4 Plugin-Exposed agents).",
    })
    _fires(run(tmp_path), "D5")


def test_near_miss_spelling_agentic_fires_d4(tmp_path):
    # "39-agentic" must not count as a bound "N-agent" token
    _write(tmp_path, plugin={
        "name": "f", "description": "A 39-agentic workflow suite."
    })
    _fires(run(tmp_path), "D4")


def test_near_miss_spelling_singular_role_fires_d4(tmp_path):
    # "39 prompt role" (singular) is not the licensed plural spelling
    _write(tmp_path, plugin={
        "name": "f", "description": "A suite with 39 prompt role."
    })
    _fires(run(tmp_path), "D4")
