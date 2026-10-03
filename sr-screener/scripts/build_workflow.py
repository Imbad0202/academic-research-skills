#!/usr/bin/env python3
"""Generate a ready-to-run Workflow script (or plain prompt files) for a screening run.

Usage:
  python build_workflow.py ta --work W --protocol screening_protocol.md --config screening_config.json \
         --jobs all|pilot|pending|recheck|recheck-all [--batches b001,b007] [--pilot-n 4]
  python build_workflow.py ft --work W --protocol ft_protocol.md --config screening_config.json --jobs all|pending

Options:
  --out FILE           where to write the script (default: W/runs/<stage>_<jobs>_NN.workflow.js)
  --emit-prompts DIR   also write one prompt file per agent call (for runs with the Agent tool
                       or by hand); an index.json lists label, prompt file and model
  --return-decisions   make the workflow also return every decision (small runs only)
  --pilot-override R   screen outside the pilot without a passing human-labelled pilot; the reason
                       is recorded in W/pilot_override.json and reported in the methods text

The full title/abstract run and pending jobs outside the recorded pilot batches need
W/pilot_check.json from merge_decisions.py --pilot-labels: every labelled pilot record must
have been compared and the AI must not have excluded any record the team advanced.
Pilot-only retries remain available before the check passes. Generate a pilot workflow first
to record its batches in W/pilot_batches.json.

The protocol text is embedded verbatim; the reviewer wording comes from templates/prompts.md.
Run the result with the Workflow tool: Workflow({scriptPath: "<printed path>"}).
"""
import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import srlib  # noqa: E402


def load_prompts():
    text = open(os.path.join(srlib.skill_dir(), "templates", "prompts.md"), encoding="utf-8").read()
    blocks = dict(re.findall(r"<!-- prompt:([a-z_]+) -->\n(.*?)\n<!-- /prompt -->", text, flags=re.S))
    need = ["reviewer_intro", "rules_ta", "rules_ft", "protocol_wrapper", "task_batch_read", "task_grep_subset",
            "adjudicator_intro", "adjudicator_tiebreak", "qc_intro", "task_ft_pdf"]
    missing = [n for n in need if n not in blocks]
    if missing:
        raise SystemExit(f"templates/prompts.md is missing blocks: {missing}")
    return blocks


def fill(tpl, vars_):
    return re.sub(r"\{\{([A-Z_]+)\}\}", lambda m: str(vars_[m.group(1)]) if m.group(1) in vars_ else m.group(0), tpl)


def codes_text(cfg, stage):
    return srlib.codes_text(cfg, stage)


def next_out(work, stage, jobs):
    d = os.path.join(work, "runs")
    os.makedirs(d, exist_ok=True)
    n = len(glob.glob(os.path.join(d, f"{stage}_*.workflow.js"))) + 1
    return os.path.join(d, f"{stage}_{jobs}_{n:02d}.workflow.js")


def batch_job(entry, width):
    nums = [int(i[1:]) for i in entry["ids"]]
    job = {"b": entry["batch"]}
    if nums == list(range(nums[0], nums[0] + len(nums))):
        job.update({"from": nums[0], "to": nums[-1]})
    else:
        job["ids"] = entry["ids"]
    return job


def ta_jobs(a, work, manifest, width):
    by_b = {m["batch"]: m for m in manifest}
    jobs = {"screen": [], "adj": [], "recheck": []}
    if a.jobs == "all":
        jobs["screen"] = [batch_job(m, width) for m in manifest]
    elif a.jobs == "pilot":
        chosen = [b.strip() for b in a.batches.split(",")] if a.batches else []
        if not chosen:
            chosen = srlib.load_json(os.path.join(work, "pilot_batches.json"), []) or []
        if not chosen:
            n = max(1, a.pilot_n)
            step = max(1, len(manifest) // n)
            chosen = [manifest[i]["batch"] for i in range(0, len(manifest), step)][:n]
            seeds = srlib.load_json(os.path.join(work, "seeds.json"), []) or []
            id2b = {i: m["batch"] for m in manifest for i in m["ids"]}
            chosen += [id2b[s["id"]] for s in seeds if s.get("id") in id2b]
        chosen = sorted(dict.fromkeys(chosen))
        unknown = [b for b in chosen if b not in by_b]
        if unknown:
            raise SystemExit(f"unknown batches: {unknown}")
        jobs["screen"] = [batch_job(by_b[b], width) for b in chosen]
    elif a.jobs == "pending":
        pend = srlib.load_json(os.path.join(work, "pending.json"))
        if pend is None:
            raise SystemExit("pending.json not found - run merge_decisions.py first")
        for p in pend.get("screen", []):
            full = by_b[p["b"]]["ids"]
            job = batch_job(by_b[p["b"]], width)
            if len(p["missA"]) == len(full) and len(p["missB"]) == len(full):
                pass  # never screened: both reviewers read the whole batch, conflicts adjudicated in this run
            else:
                job["A"] = "all" if len(p["missA"]) == len(full) else p["missA"]
                job["B"] = "all" if len(p["missB"]) == len(full) else p["missB"]
            jobs["screen"].append(job)
        jobs["adj"] = [{"b": p["b"], "items": p["items"]} for p in pend.get("adj", [])]
    elif a.jobs == "recheck":
        cand = srlib.load_json(os.path.join(work, "qc_candidates.json"))
        if cand is None:
            raise SystemExit("qc_candidates.json not found - run merge_decisions.py with QC settings first")
        jobs["recheck"] = [{"b": c["b"], "ids": c["ids"], "full": bool(c.get("full"))} for c in cand if c["ids"]]
    elif a.jobs == "recheck-all":
        jobs["recheck"] = [{"b": m["batch"], "ids": m["ids"], "full": True} for m in manifest]
    return jobs


def record_override(work, reason, problem, context, **details):
    path = os.path.join(work, "pilot_override.json")
    log = srlib.load_json(path, []) or []
    log.append({"reason": reason.strip(), "problem": problem, "context_id": context["context_id"], **details})
    srlib.save_json(path, log, indent=1)
    print(f"WARNING: {problem}; reason recorded in {path}")


def pilot_gate(work, override, context):
    """The full run starts only after a pilot checked against the team's own labels."""
    check = srlib.load_json(os.path.join(work, "pilot_check.json"))
    problem = None
    if not check:
        problem = ("no human-labelled pilot: label the pilot records yourselves (pilot_labels.csv: id,d,code,why,by), "
                   "then run merge_decisions.py --pilot-labels pilot_labels.csv")
    elif not check.get("compared"):
        problem = "pilot_check.json compares no record (the labelled records have no AI decision yet)"
    elif check.get("missed_advances"):
        problem = (f"the pilot excluded {len(check['missed_advances'])} records the team advanced "
                   "(see pilot_check.json): amend the protocol and re-run the pilot")
    elif check.get("not_screened_by_ai") or check.get("compared") != check.get("labelled"):
        problem = ("not all labelled records have been compared with an AI decision "
                   "(see pilot_check.json): finish the pilot and merge again with --pilot-labels")
    elif check.get("context_id") != context["context_id"]:
        problem = "pilot comparison is stale: the protocol, effective config or dataset changed; re-pilot"
    elif not os.path.isfile(check.get("labels_file", "")) or check.get("labels_hash") != srlib.digest(
            srlib.read_text(check["labels_file"])):
        problem = "pilot labels changed or are unavailable; merge again with --pilot-labels"
    if not problem:
        return
    if not override.strip():
        raise SystemExit(f"full run blocked: {problem}. To start anyway, pass --pilot-override \"<reason>\"; "
                         "the reason is recorded and reported in the methods text.")
    record_override(work, override, f"full run started without a passing pilot ({problem})", context)


def ft_jobs(a, work):
    if a.jobs == "all":
        man = srlib.load_json(os.path.join(work, "ft_manifest.json"))
        if man is None:
            raise SystemExit("ft_manifest.json not found - run prepare_fulltext.py first")
        return {"items": [{"id": x["id"], "pdf": x["pdf"], "title": x.get("title", "")} for x in man], "adj": []}
    if a.jobs == "pending":
        pend = srlib.load_json(os.path.join(work, "ft_pending.json"))
        if pend is None:
            raise SystemExit("ft_pending.json not found - run merge_decisions.py --stage ft first")
        return {"items": pend.get("items", []), "adj": pend.get("adj", [])}
    raise SystemExit("ft supports --jobs all|pending")


def emit_prompts(a, conf, prompts, out_dir):
    """Python mirror of the template's prompt assembly, for runs without the Workflow tool."""
    os.makedirs(out_dir, exist_ok=True)
    index = []
    stage_name = "title/abstract" if a.stage == "ta" else "full-text"
    v = {"STAGE_NAME": stage_name, "CORE": conf["core"], "CODES": conf["codesText"], "PROTOCOL": conf["protocol"]}
    rules = prompts["rules_ta"] if a.stage == "ta" else prompts["rules_ft"]

    def static(role):
        if role in ("A", "B", "FTA", "FTB"):
            persona = conf["personas"]["A" if role in ("A", "FTA") else "B"]
            intro = fill(prompts["reviewer_intro"], dict(v, PERSONA=persona))
        elif role in ("ADJ", "FTADJ"):
            intro = fill(prompts["adjudicator_intro"], v)
        else:
            intro = fill(prompts["qc_intro"], v)
        return "\n\n".join([intro, fill(rules, v), fill(prompts["protocol_wrapper"], v)])

    def write(label, role, text):
        fn = os.path.join(out_dir, label.replace(":", "_") + ".txt")
        with open(fn, "w", encoding="utf-8") as f:
            f.write(text)
        index.append({"label": label + "@" + conf["context"]["context_id"],
                      "context": conf["context"], "prompt_file": fn.replace("\\", "/"),
                      "model": conf["models"].get(role, "")})

    if a.stage == "ta":
        half = -(-conf["readLimit"] // 2)
        width = conf["idWidth"]
        for j in conf["jobs"]["screen"]:
            ids = j.get("ids") or ["R" + str(i).zfill(width) for i in range(j["from"], j["to"] + 1)]
            path = f"{conf['dir']}/{j['b']}.txt"
            for role in ("A", "B"):
                mode = j.get(role, "all")
                if mode == "all":
                    task = fill(prompts["task_batch_read"], {"FILE": path, "READ_LIMIT": conf["readLimit"],
                                                             "READ_HALF": half, "READ_NEXT": half + 1, "N": len(ids),
                                                             "FIRST": ids[0], "LAST": ids[-1]})
                elif mode:
                    task = fill(prompts["task_grep_subset"], {"FILE": path, "ID_ALTERNATION": "|".join(mode),
                                                              "AFTER": conf["grepAfter"], "N": len(mode),
                                                              "ID_LIST": ", ".join(mode)})
                else:
                    continue
                write(f"{role}:{j['b']}", role, static(role) + "\n\n" + task)
        for j in conf["jobs"]["adj"]:
            ids = [x["id"] for x in j["items"]]
            lines = "\n".join(f"- {x['id']}: Reviewer A = {x.get('A') or 'no decision'}; "
                              f"Reviewer B = {x.get('B') or 'no decision'}" for x in j["items"])
            task = (f"Records in dispute ({len(ids)}):\n{lines}\n\n"
                    + fill(prompts["adjudicator_tiebreak"], {"CORE": conf["core"]}) + "\n\n"
                    + fill(prompts["task_grep_subset"], {"FILE": f"{conf['dir']}/{j['b']}.txt",
                                                         "ID_ALTERNATION": "|".join(ids), "AFTER": conf["grepAfter"],
                                                         "N": len(ids), "ID_LIST": ", ".join(ids)}))
            write(f"ADJ:{j['b']}", "ADJ", static("ADJ") + "\n\n" + task)
        for j in conf["jobs"]["recheck"]:
            path, ids = f"{conf['dir']}/{j['b']}.txt", j["ids"]
            if j.get("full"):
                task = fill(prompts["task_batch_read"], {"FILE": path, "READ_LIMIT": conf["readLimit"], "READ_HALF": half,
                                                         "READ_NEXT": half + 1, "N": len(ids), "FIRST": ids[0],
                                                         "LAST": ids[-1]})
            else:
                task = fill(prompts["task_grep_subset"], {"FILE": path, "ID_ALTERNATION": "|".join(ids),
                                                          "AFTER": conf["grepAfter"], "N": len(ids),
                                                          "ID_LIST": ", ".join(ids)})
            write(f"QC:{j['b']}", "QC", static("QC") + "\n\n" + task)
    else:
        for x in conf["jobs"]["items"]:
            task = fill(prompts["task_ft_pdf"], {"ID": x["id"], "TITLE": x.get("title", "").replace('"', "'"),
                                                 "PDF": x["pdf"], "DISPUTE": ""})
            for role in ("FTA", "FTB"):
                if x.get(role[-1]) is not False:
                    write(f"{role}:{x['id']}", role, static(role) + "\n\n" + task)
        for x in conf["jobs"]["adj"]:
            dispute = (f"Disputed: Reviewer A = {x['A']}; Reviewer B = {x['B']}. "
                       "Decide from the report and the protocol.\n")
            task = fill(prompts["task_ft_pdf"], {"ID": x["id"], "TITLE": x.get("title", "").replace('"', "'"),
                                                 "PDF": x["pdf"], "DISPUTE": dispute})
            write(f"FTADJ:{x['id']}", "FTADJ", static("FTADJ") + "\n\n" + task)
    srlib.save_json(os.path.join(out_dir, "index.json"), index, indent=1)
    return len(index)


def main():
    srlib.utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["ta", "ft"])
    ap.add_argument("--work", required=True)
    ap.add_argument("--protocol", required=True)
    ap.add_argument("--config")
    ap.add_argument("--jobs", required=True, choices=["all", "pilot", "pending", "recheck", "recheck-all"])
    ap.add_argument("--batches", default="")
    ap.add_argument("--pilot-n", type=int, default=4)
    ap.add_argument("--out")
    ap.add_argument("--emit-prompts")
    ap.add_argument("--return-decisions", action="store_true")
    ap.add_argument("--pilot-override", default="", help="reason for starting the full run without a passing pilot")
    a = ap.parse_args()

    work = os.path.abspath(a.work)
    cfg = srlib.load_config(a.config)
    protocol = srlib.read_text(a.protocol).strip()
    if len(protocol) < 200:
        raise SystemExit("the protocol file looks empty - write and confirm it first (protocol mode)")
    prompts = load_prompts()
    recs = srlib.load_json(os.path.join(work, "records.json"))
    if recs is None:
        raise SystemExit("records.json not found - run prepare_records.py first")
    width = recs.get("id_width", 5)
    manifest = srlib.load_json(os.path.join(work, "manifest.json"), [])

    if a.stage == "ft":
        ta_ids, qc_ids, problems, uncovered, stale = srlib.fulltext_status(work, cfg)
        if ta_ids or problems or stale:
            raise SystemExit("full-text workflow blocked: finish title/abstract screening and rerun "
                             "prepare_fulltext.py for the current decisions")
    context = srlib.activate_context(work, a.stage, a.protocol, cfg)
    authorized_ids = None

    if a.stage == "ta":
        jobs = ta_jobs(a, work, manifest, width)
        pilot_batches = set(srlib.load_json(os.path.join(work, "pilot_batches.json"), []) or [])
        if a.jobs == "pilot":
            chosen = {j["b"] for j in jobs["screen"]}
            if pilot_batches and not chosen <= pilot_batches:
                if not a.pilot_override.strip():
                    raise SystemExit("pilot scope is fixed in pilot_batches.json; widening it requires "
                                     '--pilot-override "<reason>" (recorded)')
                record_override(work, a.pilot_override, "pilot scope widened", context,
                                from_batches=sorted(pilot_batches), to_batches=sorted(pilot_batches | chosen))
            pilot_batches |= chosen
            srlib.save_json(os.path.join(work, "pilot_batches.json"), sorted(pilot_batches), indent=1)
        pilot_ids = {rid for m in manifest if m["batch"] in pilot_batches for rid in m["ids"]}
        by_batch = {m["batch"]: m["ids"] for m in manifest}
        by_batch.update(srlib.load_json(os.path.join(work, "qc_batches.json"), {}) or {})
        outside_pilot = any(not set(by_batch.get(j["b"], [])) <= pilot_ids
                            for j in jobs["screen"] + jobs["adj"] + jobs["recheck"])
        if a.jobs == "all" or (a.jobs != "pilot" and outside_pilot):
            pilot_gate(work, a.pilot_override, context)
            authorized_ids = [rid for m in manifest for rid in m["ids"]]
        else:
            authorized_ids = sorted(pilot_ids)
        keep = ["reviewer_intro", "rules_ta", "protocol_wrapper", "task_batch_read", "task_grep_subset",
                "adjudicator_intro", "adjudicator_tiebreak", "qc_intro"]
        n_calls = 2 * len(jobs["screen"]) + len(jobs["adj"]) + len(jobs["recheck"])
        size = f"{len(jobs['screen'])} batch jobs, {sum(len(j['items']) for j in jobs['adj'])} disputed records, " \
               f"{sum(len(j['ids']) for j in jobs['recheck'])} records to recheck"
    else:
        jobs = ft_jobs(a, work)
        keep = ["reviewer_intro", "rules_ft", "protocol_wrapper", "task_ft_pdf", "adjudicator_intro"]
        n_calls = 2 * len(jobs["items"]) + len(jobs["adj"])
        size = f"{len(jobs['items'])} reports, {len(jobs['adj'])} disputed reports"
    if not n_calls:
        raise SystemExit("nothing to run for these --jobs (already complete?)")

    conf = {
        "stage": a.stage,
        "tool": f"{srlib.TOOL} {srlib.VERSION}",
        "protocol": protocol,
        "prompts": {k: prompts[k] for k in keep},
        "core": " AND ".join(cfg["core_criteria"]),
        "codes": srlib.exclusion_codes(cfg, a.stage),
        "codesText": codes_text(cfg, a.stage),
        "personas": cfg["personas"],
        "models": cfg["models"],
        "agentType": cfg.get("agent_type") or "",
        "conflictPolicy": cfg["conflict_policy"] if a.stage == "ta" else "adjudicate",
        "dir": os.path.join(work, "batches").replace("\\", "/"),
        "idWidth": width,
        "readLimit": int(cfg.get("read_limit", 900)),
        "grepAfter": max(int(cfg.get("grep_after", 60)),
                         (srlib.load_json(os.path.join(work, "identification.json"), {}) or {}).get("max_record_lines", 0) + 2),
        "returnDecisions": bool(a.return_decisions),
        "jobs": jobs,
        "context": context,
        "batchIds": by_batch if a.stage == "ta" else {},
        "authorizedIds": authorized_ids,
    }
    tpl_name = "ta_screening.template.js" if a.stage == "ta" else "ft_screening.template.js"
    tpl = open(os.path.join(srlib.skill_dir(), "templates", "workflows", tpl_name), encoding="utf-8").read()
    if "__SR_CONFIG__" not in tpl:
        raise SystemExit(f"template {tpl_name} lacks the __SR_CONFIG__ marker")
    script = tpl.replace("__SR_CONFIG__", json.dumps(conf, ensure_ascii=True, indent=1))
    out = os.path.abspath(a.out) if a.out else next_out(work, a.stage, a.jobs)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(script)

    print(f"workflow script: {out}")
    print(f"jobs: {size}")
    print(f"planned agent calls: about {n_calls} (+ retries for missing decisions"
          + (", + one adjudication call per batch with conflicts)" if a.stage == "ta" and jobs["screen"] else ")"))
    shown_models = {r: m or "session model (explicit override)" for r, m in cfg["models"].items()}
    print(f"models: {json.dumps(shown_models)}  agentType: {conf['agentType'] or '(default workflow subagent)'}")
    over = srlib.model_overrides(cfg)
    if over:
        print(f"model overrides from screening_config.json (shipped default is sonnet): {json.dumps(over)}")
    print(f'next: Workflow({{scriptPath: "{out.replace(chr(92), "/")}"}})  - only after the user approves the cost')
    if a.emit_prompts:
        n = emit_prompts(a, conf, prompts, os.path.abspath(a.emit_prompts))
        print(f"prompt files: {n} written to {os.path.abspath(a.emit_prompts)} (see index.json)")


if __name__ == "__main__":
    main()
