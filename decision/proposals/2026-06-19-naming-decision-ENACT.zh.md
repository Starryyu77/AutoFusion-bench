# 命名决定：ENACT（2026-06-19）

**决定**：项目 / benchmark 对外名称定为 **ENACT**，取代 AutoFusion-Bench（后者作为融合方法的联想已被专家否定）。

## 含义

- **词义**：to enact = 把决定付诸行动 —— 直接对应核心问题"模型能否把对证据的诊断付诸正确行动"。
- **Backronym**：**EvideNce-to-ACTion**（E-N-ACT），把 diagnosis-to-action 嵌进名字本身。

## 一句话 tagline

> Do multimodal LLMs **enact** their own diagnosis of unreliable audio-visual evidence?

## 候选论文标题

1. **ENACT: Do Multimodal LLMs Act on Their Own Diagnosis of Unreliable Audio-Visual Evidence?**
2. **ENACT: Benchmarking the Diagnosis-to-Action Gap in Multimodal LLMs**
3. **ENACT: Evidence-to-Action Evaluation of Multimodal LLMs under Unreliable Audio-Visual Evidence**

## 为什么是它

- 旧名 "AutoFusion" 误导为"融合方法"（专家已指出）；
- **不用 Triage / Diagnosis 打头**——诊断不是新颖点，行动才是；triage 名会自我矮化；
- ENACT 把唯一不可替代的卖点（按自己诊断行动 / CPF + rule_lift）写进名字；
- 与治理派（AVEG/EGAV）、直白派（D2A）相比，记忆点和叙事张力最强。

## 撞名核实状态

- 2026-06-19 搜索 "ENACT benchmark multimodal LLM evaluation" **未发现同名 benchmark**；
- 锁定 camera-ready 前应再做一次 arXiv / Google Scholar 终检（守 Rule 4）。

## 传播范围建议

- **立即**：作为论文 / benchmark 名启用（title、abstract、figure、proposal、主表标题）。
- **暂缓**：repo 目录名与 GitHub 仓库改名留到 AAAI 投稿后（避免 crunch 期 churn；GitHub 改名须你本人操作）。
- **过渡期**：repo 仍叫 `AutoFusion-bench`，文档对外名用 ENACT，可加一行 "ENACT (working repo: AutoFusion-bench)"。
