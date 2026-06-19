# Mini-Pilot Gold-Freeze 裁决方案（2026-06-19）

> 状态：Decision-Team 准备文档。AI agent 已备好规则、媒体修复、以及逐行建议处置。
> **gold 冻结本身是 TianYu 的决定**（依 EXPERIMENT_CONSTITUTION）。
> 下列建议在冻结 `mini_pilot.gold.jsonl` 前需对照实际媒体确认。

## 0. 两个 blocker，按优先级

1. **媒体 bug（任何模型调用前必须修）。** 5 个 `audio_mute` 污染文件**完全没有音轨**（只有视频流）。
   加噪文件则正确保留 `aac` 音轨。这是输入契约不一致，也是 artifact 捷径
   （模型可能仅凭"没有音轨"就推断"这是 mute 条件"）。
2. **17 行卡在裁决**（3 oracle-route、1 unclear、13 partial）。
   解决它们决定 headline 集是否有足够的非平凡行来显出 gap（见 headline-metric 文档 §4）。

## 1. 媒体修复：把 mute 重编码为"有音轨但静音"，而非"删音轨"

ffprobe 确认（2026-06-19），五个全是 video-only：
`src_001__音频静音`、`src_004__音频静音`、`src_006__音频静音`、
`src_007__音频静音`、`src_010__音频静音`。

**决定：** `audio_mute` 应指*有音轨但静音*（振幅清零，codec/采样率/时长与 clean 一致），
而非*删除音轨*。理由：(a) 这样每种污染类型都保持相同的 video+audio 容器，"没有音轨"就不能当捷径；
(b) omni 模型仍收到音频通道，必须把它*诊断*为静音，这才是真正的证据诊断能力；
(c) 它在标注层面与 data-spec 示例（`modality_quality_status.audio = missing`、`makes_unanswerable`）一致，
同时不改变容器契约。

精确命令（逐文件，非破坏性——写入 `.fixed.mp4`）：

```bash
ffmpeg -y -i clean/<src>.mp4 -map 0:v -map 0:a \
  -c:v copy -af volume=0 -c:a aac -shortest \
  corrupted/_audio_mute_fixed/<src>__音频静音.mp4
```

当 ffprobe 显示 `h264` + `aac` 且 `mean_volume ≈ -91 dB` 后，换入修正文件并重跑 validator。
标注**不**变。

> 已执行（2026-06-19）：5 个修正文件已生成在 `data/media/mini_pilot/corrupted/_audio_mute_fixed/`，
> ffprobe 验证全部含 h264+aac、mean_volume −91dB、时长与 clean 一致。原文件未动；确认后替换即可。

## 2. 裁决规则（按此顺序应用，否则默认 exclude）

| 规则 | 条件 | 处置 |
|---|---|---|
| **A. 无关污染升级** | 污染命中对该 source 问题*无关*的模态（如对 `video_only` source 加音频噪声） | `answerable`；`recoverability=not_needed`；`corruption_relevance=answer_irrelevant`；`corruption_effect=no_effect`；`preferred_route=[干净模态]`。**保留为 headline——这是 false-alarm 控制。** |
| **B. 干净恢复升级** | 被污染的不是必要模态；另一干净模态支持 gold 答案 | `answerable`；`recoverability=recoverable`；`recovery_source=[另一模态]`；`preferred_route=[另一模态]`。**保留为 headline——研究关键。** |
| **C. 必要模态退化** | 污染命中必要模态 | severe → `unanswerable`+`abstain=true`（headline，abstention 测试）；mild 但明显仍可用 → `answerable` 配退化 route；确实边界 → exclude |
| **D. Oracle-route 修复** | 可答但 `preferred_route` 为空 | 用 A/B/C 设 route；若两模态都仍需要且可用 → `[audio,video]`；无法判定 → exclude |
| **E. Unclear** | 任何 `unclear` 字段 | 复看媒体后按主导证据裁决；仍 unclear → exclude |
| **F. 默认** | 以上都不干净适用 | `exclude_from_main`（保留既有"partial→exclude"可靠性规则） |

## 3. 17 行卡住样本的建议处置

依据 问题 + gold + source 模态标签 推断；**需对照媒体确认。**
"→ HEADLINE" 表示应救回硬打分，而非排除。

### Oracle-route 修复（3）
| 行 | Source | 建议 | 规则 |
|---|---|---|---|
| `src_005__视频轻度模糊` | av_joint | 若仍需 joint route=`[audio,video]`，否则取干净模态 → HEADLINE | D |
| `src_005__音频轻度加噪` | av_joint | 可能 route=`[video]`（音频只是轻度噪声）→ HEADLINE | D/B |
| `src_006__音频重度加噪` | av_joint | severe 音频 + joint → 可能 `unanswerable`/abstain 或 exclude | D/C |

### Unclear（1）
| 行 | Source | 建议 | 规则 |
|---|---|---|---|
| `src_001__视频重度模糊`（"人们在做什么"，gold=Practice oral skills） | audio_only | 视频模糊但 source 是 audio-only → 答案可从音频恢复 → `answerable`,`recoverable`,route=`[audio]` → **HEADLINE（绝佳 gap 案例）** | E/B |

### Partial（13）—— 按规则分组
**可能是无关污染控制 → 升级为 HEADLINE（规则 A）：**
`src_007__音频重度加噪`、`src_008__音频轻度加噪`（对 `video_only` source 的音频污染，而答案需视频）。

**可能是干净恢复 → 升级为 HEADLINE（规则 B）：**
`src_001__视频轻度遮挡`、`src_002__视频重度遮挡`（视频被污染，答案可从 audio-only source 的音频恢复）。

**必要模态退化 / conflict —— 裁决严重度（规则 C），其中几条是最有料的 conflict 行：**
`src_002__音频重度加噪`、`src_003__视频重度模糊`、`src_007__视频轻度遮挡`、
`src_008__视频轻度模糊`、`src_009__视频轻度模糊`、`src_009__音频轻度加噪`、
`src_009__音频重度加噪`、`src_010__音频轻度加噪`、`src_001__音频轻度加噪`。

> 优先*裁决救回* `src_009` / `src_010` 这些 conflict-candidate 行，而非排除——
> 它们是 gap 指标价值最高的行。

## 4. 裁决后 headline 集的预估

- 当前干净 headline 候选：17。
- 经规则 A/B 可救回（控制 + 恢复）：约再 4-6。
- 合计：约 21-23 行 headline，其中相当一部分是非平凡的（恢复 + 无关控制 + conflict）。
  仍然偏小：把 mini-pilot CPF 当**存在性证据**，不要当可引用比率（headline-metric 文档 §4）。
  CPF 数值只在 40-source pilot 报告。

## 5. 给 TianYu 的决定清单（二元选择）

1. 批准"有音轨静音"修复 + 替换？（y/n）
2. 批准规则 A 升级（无关污染行 → headline 控制）？（y/n）
3. 批准规则 B 升级（干净恢复行 → headline）？（y/n）
4. `src_009`/`src_010` 每条 conflict 行：污染后可用 还是 exclude？（逐行）
5. `src_006__音频重度加噪`：abstain-headline 还是 exclude？

回答完 1-5 后，agent 重生成 export、跑 validator、冻结 `mini_pilot.gold.jsonl`，
并端到端跑 diagnosis / real action / fixed-rule 控制 / scorer。
