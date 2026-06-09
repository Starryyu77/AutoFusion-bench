# 标注字段填写指南

这份指南解释网站里每个关键字段怎么选。

## 1. source_decision

先看 clean source，也就是未污染的原始视频/音频。

| 值 | 什么时候选 |
|---|---|
| `accept` | 原始媒体清楚支持 gold answer |
| `reject` | 原始媒体不支持答案、答案疑似错、或者只靠常识猜 |
| `adjudicate` | 你不确定，需要负责人复核 |

硬规则：如果 clean source 不是 `accept`，对应 corrupted instances 不进主测评。

## 2. post_corruption_answerability

看 corrupted media 后判断还能不能回答。

| 值 | 什么时候选 |
|---|---|
| `answerable` | 污染后仍有清楚证据支持某个答案 |
| `partially_answerable` | 有一些证据，但不够稳定或需要经验判断 |
| `unanswerable` | 证据不足，可靠系统应该拒答 |
| `unclear` | 你判断不了 |

## 3. main_answerability

这是决定是否进入主测评的字段。

| 值 | 什么时候选 |
|---|---|
| `answerable` | 清楚可答，进入主测评 |
| `unanswerable` | 清楚不可答，进入主测评，用于测拒答 |
| `exclude_from_main` | 模糊、partial、争议、低置信度，不进主测评 |

## 4. cross_modal_recoverability

判断缺失/损坏的信息能不能从另一个模态补回来。

| 值 | 什么时候选 |
|---|---|
| `recoverable` | 被污染的关键信息能从另一个模态明确恢复 |
| `partially_recoverable` | 只能部分恢复，或者证据不够强 |
| `unrecoverable` | 另一个模态也补不回来 |
| `not_needed` | 不需要补偿，比如被污染的是无关模态，或原模态仍足够 |
| `unclear` | 判断不了 |

硬规则：如果你不能指出证据来源，不要选 `recoverable`。

## 5. recovery_source

如果需要或可以用某个模态补偿，填：

```json
["audio"]
```

或：

```json
["video"]
```

或：

```json
["audio", "video"]
```

如果不需要补偿或不可恢复，填空数组：

```json
[]
```

## 6. oracle_policy_action

这是“理想系统应该怎么做”。

### acceptable_routes

哪些 route 可以接受。例如音频足够，音频+视频也不坏：

```json
[["audio"], ["audio", "video"]]
```

如果应该拒答：

```json
[]
```

### preferred_route

最推荐的 route，只填一个 route：

```json
["audio"]
```

或：

```json
["video"]
```

如果应该拒答：

```json
[]
```

### disallowed_routes

哪些 route 不应该用。例如视频被污染且误导：

```json
[["video"]]
```

如果没有明确禁止，可以填：

```json
[]
```

### abstain

| 值 | 什么时候选 |
|---|---|
| `true` | 证据不足，可靠系统应该拒答 |
| `false` | 证据足够，可以回答 |

### expected_answer

- 如果 `abstain=false`，填 gold answer，必须和选项文本一致。
- 如果 `abstain=true`，填空或 `null`。

## 7. annotation_confidence

| 值 | 什么时候选 |
|---|---|
| `high` | 很确定 |
| `medium` | 基本确定，但有一点不确定 |
| `low` | 不确定，不应该进主测评 |

## 8. instance_decision

| 值 | 什么时候选 |
|---|---|
| `accept` | 可以进入主测评 |
| `reject` | 不适合这个 benchmark |
| `adjudicate` | 需要负责人复核 |

建议：

- `partial` 或 `unclear` 的样本选 `adjudicate`。
- clean source 有问题的样本选 `reject`。
- 不要为了凑数量硬选 `accept`。

## 9. 常见例子

### 例子 A：音频被静音，问题问声音来源

- `post_corruption_answerability=unanswerable`
- `cross_modal_recoverability=unrecoverable`
- `oracle_abstain=true`
- `acceptable_routes=[]`
- `preferred_route=[]`
- `expected_answer=null`

### 例子 B：视频被模糊，但问题问声音来源

- `post_corruption_answerability=answerable`
- `cross_modal_recoverability=not_needed`
- `recovery_source=[]`
- `preferred_route=["audio"]`
- `expected_answer=<gold answer>`

### 例子 C：音频错位，但视频足够回答

- `post_corruption_answerability=answerable`
- `cross_modal_recoverability=not_needed` 或 `recoverable`
- `preferred_route=["video"]`
- `disallowed_routes` 视情况包含 `[["audio"]]`
