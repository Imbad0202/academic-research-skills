---
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
runs: 3
---
ICLR reviews came back for our paper "Curriculum-Ordered Data Mixing for Small Language Model Pretraining". Scores 5 / 6 / 3. The rebuttal window closes in five days. Should we push back, and on what? Reviews are below.

For the record: the baseline and our method used the same token budget at both model sizes (Table 1, row 2 states this explicitly). We do NOT have the compute to train a 1B model within five days. We have not run anything new since submission.

-----
Reviewer A (score 5, confidence 3)
Strengths: The motivation is clear and the writing is easy to follow. The ordering heuristic is simple to implement.
Weaknesses: Only 125M and 350M models are evaluated. It is unclear whether the gains hold at 1B or beyond, which limits the significance.
Questions: Does the curriculum schedule interact with the learning-rate warmup? A short ablation would help.

Reviewer B (score 6, confidence 4)
Strengths: Good ablation coverage over ordering granularity. The compute-matched comparison in Table 1 is appreciated.
Weaknesses: There is no comparison to a learned reweighting baseline such as MixTune (2025), which targets the same problem from a different angle.
Questions: What is the wall-clock overhead of computing the ordering before training?

Reviewer C (score 3, confidence 4)
Weaknesses: (1) The baseline appears undertrained: it seems to use fewer tokens than the proposed method, so the comparison is unfair. The authors must rerun the baseline with matched tokens at both scales. (2) The paper claims "state of the art" in the abstract, but Table 3 shows a prior method scoring higher on 2 of the 6 benchmarks. This claim should be removed.
-----
