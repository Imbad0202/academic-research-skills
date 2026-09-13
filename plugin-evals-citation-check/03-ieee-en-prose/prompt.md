---
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
model: sonnet
runs: 3
---
Check the citations in this manuscript excerpt. IEEE style. Below are (a) the manuscript excerpt, (b) the reference list, and (c) a source pack listing every paper I have on file (title, authors, year, venue, abstract as published). The source pack is complete; anything not in it, I do not have.

## (a) Manuscript excerpt

Energy-aware scheduling for edge clusters has been studied from both the placement and the frequency-scaling side [1]. Reinforcement-learning schedulers report the largest gains under bursty load [3], while heuristic approaches remain competitive on steady workloads [2]. Latency-bounded offloading was formalised by Petrov and Sandoval [4], who showed that a two-tier deadline model suffices for most video-analytics pipelines. Most notably, [5] demonstrated a 38% energy reduction in production deployments, which motivates our choice of a similar DVFS policy. Cross-cluster migration adds further savings at the cost of network overhead [6], and container cold-start effects are analysed in [7].

## (b) Reference list

[1] L. Haddad and Y. Ostrowski, "A survey of energy-aware scheduling for edge clusters," *IEEE Trans. Edge Comput.*, vol. 4, no. 2, pp. 110–129, 2021, doi: 10.5555/tec.2021.0402.
[2] M. Quintero, "Heuristic placement under steady load," in *Proc. Int. Conf. Edge Syst.*, 2020, pp. 44–51, doi: 10.5555/ices.2020.0044.
[3] F. Adeyinka, S. Bao, and R. Costa, "Deep RL scheduling for bursty edge workloads," *J. Distrib. Comput.*, vol. 58, no. 7, pp. 901–917, 2022, doi: 10.5555/jdc.2022.5807.
[4] A. Petrov and M. Sandoval, "Latency-bounded offloading with two-tier deadlines," *IEEE Trans. Edge Comput.*, vol. 5, no. 1, pp. 12–27, 2022, doi: 10.5555/tec.2022.0501.
[5] K. Nwosu, T. Lindgren, and P. Varga, "DVFS policies for edge inference: A trace-driven study," in *Proc. Workshop Green Edge*, 2021, pp. 1–8, doi: 10.5555/wge.2021.0001.
[6] J. Marchetti and E. Oyelaran, "Cross-cluster migration for energy savings," *J. Distrib. Comput.*, vol. 57, no. 3, pp. 300–318, 2021, doi: 10.5555/jdc.2021.5703.

## (c) Source pack

1. **A survey of energy-aware scheduling for edge clusters** — L. Haddad, Y. Ostrowski (2021). IEEE Trans. Edge Comput. 4(2):110–129. Abstract: Surveys 84 papers on placement, frequency scaling, and workload consolidation for edge clusters; proposes a taxonomy along the placement/DVFS axis.
2. **Heuristic placement under steady load** — M. Quintero (2020). Proc. Int. Conf. Edge Syst., pp. 44–51. Abstract: Evaluates four greedy placement heuristics on steady synthetic workloads; the best heuristic is within 6% of an ILP optimum.
3. **Deep RL scheduling for bursty edge workloads** — F. Adeyinka, S. Bao, R. Costa (2022). J. Distrib. Comput. 58(7):901–917. Abstract: A PPO-based scheduler reduces energy by 22–31% relative to heuristics on bursty traces while meeting deadlines.
4. **Latency-bounded offloading with two-tier deadlines** — R. Ishikawa, D. Mbeki (2022). IEEE Trans. Edge Comput. 5(1):12–27. Abstract: Formalises latency-bounded offloading with a two-tier (soft/hard) deadline model and shows it covers the video-analytics pipelines in a public benchmark.
5. **DVFS policies for edge inference: A trace-driven study** — K. Nwosu, T. Lindgren, P. Varga (2021). Proc. Workshop Green Edge, pp. 1–8. Abstract: Using simulated traces from a public dataset, a deadline-aware DVFS policy reduces energy by up to 38% relative to performance governors. A preliminary deployment on two physical nodes is described in the appendix and left for future work.
6. **Cross-cluster migration for energy savings** — J. Marchetti, E. Oyelaran (2021). J. Distrib. Comput. 57(3):300–318. Abstract: Live migration across three clusters yields 9–14% additional savings, offset by network overhead above 40% utilisation.
