# AAAI-27 投稿时间线与决策门（2026-06-19）

> 策略：**主轨为目标 + 明确后备**（不为 deadline 牺牲数据质量，守 Rule 5）。
> 用质量门控的检查点决定"继续冲 AAAI / 转后备"，而不是盲目赶。

## 0. 硬日期

- **AAAI-27 主技术轨：摘要 2026-07-20、全文 2026-07-27（UTC-12）。** 会议 2027-02-16–23，蒙特利尔。
- 今天 2026-06-19 → 距全文截稿约 **5.5 周**。
- EAAI-27（09-08）是教育方向，不匹配，不作备选。

## 1. AAAI AI 政策合规要点

- LLM **生成正文被禁**，除非作为实验分析的一部分。
- 用 AI **编辑/润色作者本人写的文字允许**。
- AI 不能当作者，也不能当可引用来源。
- 对本项目：Qwen 的 diagnosis/action 输出属于实验内容（允许）；用 agent 润色你写的 prose（允许）。
  正文必须你写，引用必须你查证（见 `decision/literature/` positioning §3 的待核实清单）。

## 2. 后备 venue 阶梯（截稿后由近到远）

| Venue | 截稿（预估） | 相对 AAAI-27 | 定位 |
|---|---|---|---|
| **ICLR 2027** | ~2026-09 下旬（历史 9/24–10/1，CFP 未正式公布） | +约 2 个月 | 近期兜底，ML 顶会收 benchmark；给 pilot 多 2 个月 |
| **NeurIPS 2027 Evaluations & Datasets** | ~2027-05（摘要；2026 档为 5/4–5/6，已过） | +约 10 个月 | benchmark 的理想归宿；可从容做满 40-source + text 扩展 |
| （*ACL via ARR） | ARR 约每 2 月一轮；2026-10/12 轮 → ACL 2027 | +2–6 个月 | 备选，含 ARR 评审周期延迟 |

> 注：ICLR 2027 / NeurIPS 2027 日期为按历史规律预估，CFP 正式公布前以官网为准。

## 3. 三个质量门（决定冲刺 or 转后备）

### Gate 1 — 本周（~06/25）：mini-pilot 信号门
- 完成：冻结 `mini_pilot.gold.jsonl` + scorer 跑通。
- **通过标准**：存在可解释的 diagnosis-to-action 案例（CPF>0 存在性、rule_lift≥0、有清晰 failure case），且数据质量站得住。
- **不通过**：信号不清 / 数据质量差 → AAAI-27 主轨基本放弃，重新设计或直接走 NeurIPS 2027（有时间打磨）。

### Gate 2 — ~07/06：数据完备门（决定 AAAI vs 转 ICLR）
- 完成：pilot 数据 + 标注 + 裁决完成且 inter-annotator agreement 达标，scorer 主表产出。
- **通过**：07/06 前数据完备且质量达标 → 锁 AAAI-27，07/06–07/27 写作。
- **不通过**：07/06 数据未完备 / 质量存疑 → **转 ICLR 2027**（~9 月，多 2 个月），不在坏数据上赶写作。

### Gate 3 — ~07/18：草稿门
- 完成：全文初稿 + 图（Fig 1 gap 示例 + 主结果）+ `pre-submission-reviewer` 过一遍；07/20 注册摘要。
- **通过**：草稿扎实 → 07/27 投。
- **不通过**：草稿单薄 → 转 ICLR 2027。

## 4. 倒排周计划（冲刺路径）

| 周 | 重点 | 产出 |
|---|---|---|
| 06/19–06/25 | Gate 1：裁决 + mute 替换 + 冻结 gold + scorer | mini-pilot 信号判定 |
| 06/26–07/06 | 若 go：扩样 + 模型跑 + 标注/裁决（并行） | pilot 数据 + 主表（Gate 2） |
| 07/07–07/13 | 写 method + experiments；起草 related-work/intro（用已写文档） | 半稿 |
| 07/14–07/18 | 补图 + 全文润色 + pre-submission-reviewer | 全稿（Gate 3） |
| 07/19–07/27 | 收尾 + 摘要注册(07/20) + 投稿(07/27) | 提交 |

## 5. 不可牺牲的质量底线（守 Rule 5）

- CPF / rule_lift 必须来自真实 scorer 运行，绝不编造；mini-pilot 规模只报存在性证据。
- 标注一致性 / adjudication 要如实报告，partial/unclear 不进 headline。
- 不为页数或 deadline 砍掉 irrelevant-corruption 控制、clean-hard 控制、oracle 上限等关键对照。
- 任一门"不通过"就转后备，不硬投。

## 6. 立即下一步

Gate 1 卡在 gold freeze 上 → 需要你回 `2026-06-19-gold-freeze-adjudication-plan` §5 的 5 个决定
（mute 替换 / Rule A 升级 / Rule B 升级 / src_009·010 conflict 逐行 / src_006 取舍）。
回完我就本周冻结 gold + 跑 scorer，给出 Gate 1 判定。
