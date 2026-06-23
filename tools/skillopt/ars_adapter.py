"""SkillOpt environment adapter for the ARS rq_framing_patterns advisory.

Trains a compact natural-language *skill* that decides whether ARS's Socratic
wording-pattern advisory should fire for a proposed research question — the same
judgment ARS ships today as a fixed regex detector
(``scripts/check_rq_framing_patterns.py``), but expressed as an LLM skill that can
generalise to wording the 20 hardcoded shells (WP01-WP20) never anticipated.

The rollout is single-turn: for each gold item we put the (trainable) skill in the
system prompt behind a fixed output-format contract, ask the target model to judge
one RQ, parse ``trigger_advisory`` out of the answer, and score it against the gold
label. Scoring + the metric live in ``ars_scoring.py`` (pure, offline-testable);
this file is only the SkillOpt-facing glue.

Registered under the env key ``ars_rq_framing_patterns`` by ``run_ars_skillopt.py``.
"""
from __future__ import annotations

import json
import os

from skillopt.datasets.base import BatchSpec
from skillopt.envs.base import EnvAdapter
from skillopt.gradient.reflect import run_minibatch_reflect
from skillopt.model import chat_target

from tools.skillopt.ars_gold_loader import ARSRQFramingLoader
from tools.skillopt.ars_scoring import POSITIVE_LABEL, NEGATIVE_LABEL, score_prediction

# Fixed harness scaffold around the trainable skill. The skill itself is the only
# part SkillOpt edits; the format contract below is held constant so the optimizer
# can never "win" by training the output format away.
_SYSTEM_TEMPLATE = """\
You are an academic research-question (RQ) wording advisor for the ARS pipeline.

Apply the SKILL below to decide whether the Socratic wording-pattern advisory
should fire for a single proposed research question. Judge WORDING ONLY: surface
phrasing, not the idea's quality, novelty, feasibility, or topic. A broad topic
phrased specifically must NOT trigger; a narrow topic wrapped in a generic
template shell SHOULD trigger.

=== SKILL ===
{skill_content}
=== END SKILL ===

Think briefly, then end your reply with EXACTLY one final line:
  ADVISORY: YES   -> the RQ uses an AI-typical wording shell; the advisory fires
  ADVISORY: NO    -> the wording is specific / domain-native; no advisory
"""

_USER_TEMPLATE = (
    'Proposed research question:\n"{text}"\n\n'
    "Does the wording-pattern advisory fire? Give your verdict."
)


class ARSRQFramingAdapter(EnvAdapter):
    """Environment adapter for the rq_framing_patterns wording advisory."""

    def __init__(
        self,
        split_dir: str = "",
        data_path: str = "",
        split_mode: str = "ratio",
        split_ratio: str = "5:2:3",
        split_seed: int = 42,
        split_output_dir: str = "",
        exec_timeout: int = 120,
        workers: int = 8,
        analyst_workers: int = 8,
        failure_only: bool = False,
        minibatch_size: int = 8,
        edit_budget: int = 4,
        seed: int = 42,
        limit: int = 0,
        max_completion_tokens: int = 2048,
    ) -> None:
        self.exec_timeout = exec_timeout
        self.workers = workers
        self.analyst_workers = analyst_workers
        self.failure_only = failure_only
        self.minibatch_size = minibatch_size
        self.edit_budget = edit_budget
        self.max_completion_tokens = int(max_completion_tokens)
        self.dataloader = ARSRQFramingLoader(
            split_dir=split_dir,
            data_path=data_path,
            split_mode=split_mode,
            split_ratio=split_ratio,
            split_seed=split_seed,
            split_output_dir=split_output_dir,
            seed=seed,
            limit=limit,
        )

    # ── Lifecycle ──────────────────────────────────────────────────────
    def setup(self, cfg: dict) -> None:
        super().setup(cfg)
        self.dataloader.setup(cfg)

    def get_dataloader(self):
        return self.dataloader

    # ── Batch -> env manager ───────────────────────────────────────────
    def build_env_from_batch(self, batch: BatchSpec, **kwargs):
        return list(batch.payload or [])

    def build_train_env(self, batch_size: int, seed: int, **kwargs):
        batch = self.dataloader.build_train_batch(batch_size=batch_size, seed=seed, **kwargs)
        return self.build_env_from_batch(batch, **kwargs)

    def build_eval_env(self, env_num: int, split: str, seed: int, **kwargs):
        batch = self.dataloader.build_eval_batch(env_num=env_num, split=split, seed=seed, **kwargs)
        return self.build_env_from_batch(batch, **kwargs)

    # ── Rollout ────────────────────────────────────────────────────────
    def rollout(self, env_manager, skill_content: str, out_dir: str, **kwargs) -> list[dict]:
        """Classify each RQ under the current skill and score against the gold label.

        Sequential by design: the gold set is tiny (<=40 items) and a model call
        per item is IO-bound but cheap, so we trade throughput for a small, easy
        to audit loop. Each model failure degrades to a scored miss rather than
        crashing the batch.
        """
        items: list[dict] = env_manager
        results: list[dict] = []
        for item in items:
            text = item.get("question", "")
            label = item.get("label", "")
            system = _SYSTEM_TEMPLATE.format(skill_content=skill_content.strip())
            user = _USER_TEMPLATE.format(text=text)
            try:
                response, _raw = chat_target(
                    system=system,
                    user=user,
                    max_completion_tokens=self.max_completion_tokens,
                    timeout=self.exec_timeout,
                )
            except Exception as exc:  # model/transport failure -> scored miss
                response = ""
                score = score_prediction("", label)
                score["fail_reason"] = f"target_call_error: {type(exc).__name__}: {exc}"
            else:
                score = score_prediction(response, label)

            results.append({
                "id": str(item.get("id", "")),
                "question": text,
                "label": label,
                "task_type": item.get("task_type", label),
                "predicted_answer": (response or "")[:2000],
                "hard": score["hard"],
                "soft": score["soft"],
                "predicted_trigger": score["predicted_trigger"],
                "expected_trigger": score["expected_trigger"],
                "parsed_ok": score["parsed_ok"],
                "fail_reason": score["fail_reason"],
            })

        self._dump_records(out_dir, results)
        return results

    # ── Reflect ────────────────────────────────────────────────────────
    def reflect(self, results: list[dict], skill_content: str, out_dir: str, **kwargs) -> list[dict | None]:
        """Turn scored rollouts into skill-edit proposals via the shared analyst.

        Delegates to SkillOpt's standard minibatch reflection (the same path every
        built-in benchmark uses). v0.1.0 marks ``EnvAdapter.reflect`` abstract with
        no body, so we implement it explicitly rather than calling ``super()``.
        """
        return run_minibatch_reflect(
            results=results,
            skill_content=skill_content,
            prediction_dir=kwargs.get("prediction_dir", os.path.join(out_dir, "predictions")),
            patches_dir=kwargs.get("patches_dir", os.path.join(out_dir, "patches")),
            workers=self.analyst_workers,
            failure_only=self.failure_only,
            minibatch_size=self.minibatch_size,
            edit_budget=self.edit_budget,
            random_seed=kwargs.get("random_seed"),
            error_system=self.get_error_minibatch_prompt(),
            success_system=self.get_success_minibatch_prompt(),
            step_buffer_context=kwargs.get("step_buffer_context", ""),
            update_mode=getattr(self, "_cfg", {}).get("skill_update_mode", "patch"),
        )

    @staticmethod
    def _dump_records(out_dir: str, results: list[dict]) -> None:
        """Best-effort artifact dump for debugging; never fatal."""
        if not out_dir:
            return
        try:
            os.makedirs(out_dir, exist_ok=True)
            with open(os.path.join(out_dir, "rollout_records.jsonl"), "w", encoding="utf-8") as f:
                for rec in results:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except OSError:
            pass

    # ── Stratification hint ────────────────────────────────────────────
    def get_task_types(self) -> list[str]:
        seen: list[str] = []
        for item in (self.dataloader.train_items
                     + self.dataloader.val_items
                     + self.dataloader.test_items):
            tt = str(item.get("task_type") or "")
            if tt and tt not in seen:
                seen.append(tt)
        return seen or [POSITIVE_LABEL, NEGATIVE_LABEL]
