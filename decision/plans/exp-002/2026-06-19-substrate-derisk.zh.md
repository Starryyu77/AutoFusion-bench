# 数据底座去风险评估（2026-06-19）

> 状态：Decision-Team 草稿。在确定 40-source pilot 之前处理 2026-06-19 proposal 的
> Risk 1（AVQA 可能太简单 / shortcut-solvable）。这是建议，尚未冻结决定。

## 0. 风险，精确表述

三种捷径任意一种都会废掉 benchmark：

1. **Question-only guessing** —— 仅凭问题 + 选项文本、不看媒体即可推出答案。
2. **"joint" 样本上的单模态泄漏** —— 标为 audio-video-joint，却单凭一个流即可作答。
3. **Artifact detection** —— 污染太明显，模型从噪声模式而非证据推断任务。

DAVE 的动机确认 (1)-(2) 在已有 AV benchmark 中真实存在："existing benchmarks often
suffer from strong visual bias —— answers can be inferred from visual data alone"
(arXiv 2503.09321)。

## 1. 候选底座

| 底座 | 对我们的强处 | 对我们的弱处 |
|---|---|---|
| **AVQA / AVQA-videos**（当前） | 真实场景、广度、可得（HF `juyil/AVQA-videos`）、支持单模态桶 + irrelevant-corruption 控制 | 视觉偏置 / question-only 猜测；"joint" 必要性无保证 |
| **DAVE** (arXiv 2503.09321) | **强制两模态都必要**；原子误差子类；正是为消视觉偏置而建 | 设计上两模态都必要 → 不适合单模态行和 irrelevant-corruption 行；规模小；诊断风格 |
| **FortisAVQA + MAVEN** (arXiv 2504.00487) | 首个 AVQA 鲁棒性集；改写 + head/tail 漂移消语言捷径 | 音乐域 → 场景窄；为鲁棒性评测而建，非为模态必要性切分 |
| **MUSIC-AVQA-v2 / 去偏** (arXiv 2310.06238) | 去偏的答案分布 | 音乐域；同样的窄 |

## 2. 关键认识：没有单一底座能覆盖所有桶

我们的桶需要**相反**的属性：

- audio-only / video-only / irrelevant-corruption-control 行需要**单模态必要**样本
  （污染必要模态 → 不可答；污染另一个 → 无影响）。
- audio-video-joint / conflict 行需要**两模态都必要**样本。

DAVE 对第二类理想，对第一类错。AVQA 能供第一类但需要硬门。
所以答案不是"换底座"，而是"每个桶从其属性有保证的地方取数"。

## 3. 建议

1. **保留 AVQA** 供单模态桶和 irrelevant-corruption 控制，但**加强 source gate**，
   加一个显式的 question-only 猜测筛查：用纯文本（问题+选项）尝试作答（纯文本 LLM 跑一遍 + 人工抽检），
   凡能猜中的样本剔除。这直接关掉捷径 (1)。
2. **加入一批 DAVE 取样**供 audio-video-joint 和 conflict 桶，那里"两模态都必要"
   正是我们想要、且已由构造保证的属性。这为最难、最关键的行关掉捷径 (2)。
3. **把 FortisAVQA / MUSIC-AVQA-v2 留作有据备份**（proposal 已这么说），
   若 1-2 之后 joint/互补样本仍太少再用。即便不用，也作为"我们认真对待了 AVQA 偏置"的证据引用。
4. Artifact 捷径 (3) 由 gold-freeze 方案处理（silent-track mute 修复 + irrelevant-corruption 控制
   + generator-metadata baseline），而非靠底座选择。

## 4. 为什么不直接全换成 DAVE

DAVE 的"两模态都必要"设计，会拿掉我们构造干净的单模态行和 irrelevant-corruption 行的能力，
而治理故事与 irrelevant-corruption 控制都需要这些。DAVE 强化 joint 桶，但扛不起整个 protocol。

## 5. 需要 TianYu 拍板

- 批准"AVQA（加门）+ DAVE joint 切片"的拆分，还是 mini-pilot 先维持 AVQA-only、到 40-source 门再议？
- 批准把纯文本 question-guess 筛查加进 source gate？

## 6. 核实状态

DAVE abstract 本次会话已核实 (2503.09321)。FortisAVQA (2504.00487) 与
MUSIC-AVQA-v2 去偏 (2310.06238) 见于搜索列表；取数前确认域匹配与 licensing。
