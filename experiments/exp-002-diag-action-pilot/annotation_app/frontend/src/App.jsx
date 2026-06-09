import { useCallback, useEffect, useMemo, useRef, useState } from "react";

const DEFAULT_SHEET =
  "experiments/exp-002-diag-action-pilot/annotations/smoke_annotation_sheet_v1.draft.jsonl";
const DEFAULT_EXPORT =
  "experiments/exp-002-diag-action-pilot/annotations/pilot_annotations.local.jsonl";

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return response.json();
}

function setNestedValue(value, path, nextValue) {
  const copy = structuredClone(value);
  let cursor = copy;
  for (let index = 0; index < path.length - 1; index += 1) {
    const key = path[index];
    if (cursor[key] === undefined || cursor[key] === null) {
      cursor[key] = {};
    }
    cursor = cursor[key];
  }
  cursor[path[path.length - 1]] = nextValue;
  return copy;
}

function routeLabel(route) {
  if (!Array.isArray(route) || route.length === 0) return "abstain";
  return route.join("+");
}

function statusText(status) {
  const labels = {
    needs_human_review: "待审核",
    in_progress: "处理中",
    reviewed: "已完成",
    needs_adjudication: "需仲裁",
    rejected: "剔除"
  };
  return labels[status] || status || "未知";
}

function App() {
  const [options, setOptions] = useState({});
  const [summary, setSummary] = useState(null);
  const [instances, setInstances] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [detail, setDetail] = useState(null);
  const [filter, setFilter] = useState("all");
  const [query, setQuery] = useState("");
  const [importPath, setImportPath] = useState(DEFAULT_SHEET);
  const [exportPath, setExportPath] = useState(DEFAULT_EXPORT);
  const [annotator, setAnnotator] = useState("local");
  const [message, setMessage] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  const annotation = detail?.annotation || null;

  const refreshSummary = useCallback(async () => {
    const result = await api("/api/summary");
    setSummary(result);
  }, []);

  const refreshInstances = useCallback(async () => {
    const params = new URLSearchParams();
    if (filter !== "all") params.set("status", filter);
    if (query.trim()) params.set("q", query.trim());
    const result = await api(`/api/instances?${params.toString()}`);
    setInstances(result);
    if (!selectedId && result.length > 0) {
      setSelectedId(result[0].instance_id);
    }
  }, [filter, query, selectedId]);

  const loadDetail = useCallback(async (instanceId) => {
    if (!instanceId) {
      setDetail(null);
      return;
    }
    const result = await api(`/api/instances/${encodeURIComponent(instanceId)}`);
    setDetail(result);
  }, []);

  useEffect(() => {
    api("/api/options").then(setOptions).catch((error) => setMessage(error.message));
    refreshSummary().catch(() => {});
  }, [refreshSummary]);

  useEffect(() => {
    refreshInstances().catch((error) => setMessage(error.message));
  }, [refreshInstances]);

  useEffect(() => {
    loadDetail(selectedId).catch((error) => setMessage(error.message));
  }, [selectedId, loadDetail]);

  const updateAnnotation = (path, value) => {
    setDetail((current) => {
      if (!current) return current;
      return { ...current, annotation: setNestedValue(current.annotation, path, value) };
    });
  };

  const updateWholeAnnotation = (nextAnnotation) => {
    setDetail((current) => (current ? { ...current, annotation: nextAnnotation } : current));
  };

  const importSheet = async () => {
    setMessage("导入中...");
    const result = await api("/api/import", {
      method: "POST",
      body: JSON.stringify({
        path: importPath,
        annotator,
        session_name: `local-${annotator}`,
        replace: true
      })
    });
    setMessage(`已导入 ${result.rows_imported} 行`);
    setSelectedId("");
    await refreshSummary();
    await refreshInstances();
  };

  const saveAnnotation = async (markReviewed = false) => {
    if (!annotation) return;
    setIsSaving(true);
    const body = markReviewed
      ? { ...annotation, review_status: "reviewed" }
      : annotation;
    try {
      const result = await api(`/api/instances/${encodeURIComponent(body.instance_id)}`, {
        method: "PUT",
        body: JSON.stringify({ annotation: body, annotator })
      });
      setDetail(result);
      setMessage(markReviewed ? "已保存并标记完成" : "已保存");
      await refreshSummary();
      await refreshInstances();
    } finally {
      setIsSaving(false);
    }
  };

  const exportAnnotations = async () => {
    setMessage("导出中...");
    const result = await api("/api/export", {
      method: "POST",
      body: JSON.stringify({ output_path: exportPath })
    });
    setMessage(`已导出 ${result.rows_exported} 行到 ${result.output_path}`);
  };

  const addTimeSpan = (modality, timeSeconds) => {
    if (!annotation) return;
    const start = Math.max(0, Number(timeSeconds || 0) - 1);
    const end = Math.max(start, Number(timeSeconds || 0) + 1);
    const next = structuredClone(annotation);
    next.recovery_evidence = next.recovery_evidence || {};
    next.recovery_evidence[`${modality}_time`] = { start, end };
    next.recovery_evidence.annotation_app_time_spans = [
      ...(next.recovery_evidence.annotation_app_time_spans || []),
      { modality, start, end, note: "" }
    ];
    updateWholeAnnotation(next);
  };

  const addBBox = (mediaLabel, bbox, timeSeconds) => {
    if (!annotation) return;
    const next = structuredClone(annotation);
    next.defect_location = next.defect_location || {};
    next.defect_location.bboxes = [
      ...(next.defect_location.bboxes || []),
      {
        media: mediaLabel,
        modality: "video",
        time: Number.isFinite(timeSeconds) ? timeSeconds : null,
        ...bbox
      }
    ];
    updateWholeAnnotation(next);
  };

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <h1>exp-002 本地多媒体标注</h1>
          <p>本机 SQLite 保存，导出 scorer 兼容 JSONL。</p>
        </div>
        <div className="topbar-actions">
          <input value={annotator} onChange={(event) => setAnnotator(event.target.value)} />
          <button type="button" onClick={() => saveAnnotation(false)} disabled={!annotation || isSaving}>
            保存
          </button>
          <button type="button" className="primary" onClick={() => saveAnnotation(true)} disabled={!annotation || isSaving}>
            保存完成
          </button>
        </div>
      </header>

      <section className="io-strip">
        <label>
          导入 sheet
          <input value={importPath} onChange={(event) => setImportPath(event.target.value)} />
        </label>
        <button type="button" onClick={importSheet}>导入</button>
        <label>
          导出 JSONL
          <input value={exportPath} onChange={(event) => setExportPath(event.target.value)} />
        </label>
        <button type="button" onClick={exportAnnotations}>导出</button>
        <div className="message">{message}</div>
      </section>

      <section className="workspace">
        <Sidebar
          summary={summary}
          instances={instances}
          selectedId={selectedId}
          filter={filter}
          query={query}
          onFilter={setFilter}
          onQuery={setQuery}
          onSelect={setSelectedId}
        />
        <MediaWorkspace
          annotation={annotation}
          media={detail?.media}
          onAddTimeSpan={addTimeSpan}
          onAddBBox={addBBox}
        />
        <AnnotationForm
          annotation={annotation}
          options={options}
          onChange={updateAnnotation}
          onWholeChange={updateWholeAnnotation}
        />
      </section>
    </main>
  );
}

function Sidebar({ summary, instances, selectedId, filter, query, onFilter, onQuery, onSelect }) {
  const counts = summary?.status_counts || {};
  return (
    <aside className="sidebar">
      <div className="panel-header">
        <h2>实例队列</h2>
        <span>{instances.length} rows</span>
      </div>
      <div className="status-grid">
        <button className={filter === "all" ? "active" : ""} onClick={() => onFilter("all")}>
          全部 {Object.values(counts).reduce((sum, value) => sum + value, 0)}
        </button>
        {["needs_human_review", "in_progress", "reviewed", "needs_adjudication"].map((status) => (
          <button key={status} className={filter === status ? "active" : ""} onClick={() => onFilter(status)}>
            {statusText(status)} {counts[status] || 0}
          </button>
        ))}
      </div>
      <input
        className="search"
        value={query}
        placeholder="搜索 instance / question"
        onChange={(event) => onQuery(event.target.value)}
      />
      <div className="instance-list">
        {instances.map((item) => (
          <button
            type="button"
            key={item.instance_id}
            className={`instance-row ${item.instance_id === selectedId ? "selected" : ""}`}
            onClick={() => onSelect(item.instance_id)}
          >
            <span className={`status-dot ${item.review_status}`} />
            <strong>{item.instance_id}</strong>
            <small>{item.affected_modality || "unknown"} / {item.corruption_type || "none"}</small>
            <span>{item.question}</span>
          </button>
        ))}
      </div>
    </aside>
  );
}

function MediaWorkspace({ annotation, media, onAddTimeSpan, onAddBBox }) {
  if (!annotation) {
    return <section className="media-workspace empty">先导入 annotation sheet，然后选择一个实例。</section>;
  }

  return (
    <section className="media-workspace">
      <div className="question-panel">
        <div>
          <div className="label">Question</div>
          <h2>{annotation.question}</h2>
        </div>
        <div className="answer-box">
          <span>Gold</span>
          <strong>{annotation.gold_answer || "N/A"}</strong>
        </div>
      </div>
      <div className="choices">
        {(annotation.choices || []).map((choice, index) => (
          <span key={`${choice}-${index}`}>{index + 1}. {choice}</span>
        ))}
      </div>
      <div className="media-grid">
        {(media?.items || [media?.source, media?.corrupted]).filter(Boolean).map((item) => (
          <MediaViewer
            key={`${item.label}-${item.path || "missing"}`}
            title={item.label === "source" ? "Clean source" : item.label === "corrupted" ? "Corrupted" : item.label}
            media={item}
            bboxes={annotation.defect_location?.bboxes || []}
            onAddTimeSpan={onAddTimeSpan}
            onAddBBox={onAddBBox}
          />
        ))}
      </div>
      <EvidenceList annotation={annotation} />
    </section>
  );
}

function MediaViewer({ title, media, bboxes, onAddTimeSpan, onAddBBox }) {
  const frameRef = useRef(null);
  const mediaRef = useRef(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [drawing, setDrawing] = useState(false);
  const [draftBox, setDraftBox] = useState(null);
  const [isDrawMode, setIsDrawMode] = useState(false);

  const mediaBBoxes = useMemo(
    () => (bboxes || []).filter((box) => box.media === media?.label),
    [bboxes, media?.label]
  );

  const startDraw = (event) => {
    if (!isDrawMode || !frameRef.current || media?.kind === "audio") return;
    const rect = frameRef.current.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width;
    const y = (event.clientY - rect.top) / rect.height;
    setDrawing(true);
    setDraftBox({ x, y, width: 0, height: 0 });
  };

  const moveDraw = (event) => {
    if (!drawing || !draftBox || !frameRef.current) return;
    const rect = frameRef.current.getBoundingClientRect();
    const x2 = Math.min(1, Math.max(0, (event.clientX - rect.left) / rect.width));
    const y2 = Math.min(1, Math.max(0, (event.clientY - rect.top) / rect.height));
    setDraftBox({
      x: Math.min(draftBox.x, x2),
      y: Math.min(draftBox.y, y2),
      width: Math.abs(x2 - draftBox.x),
      height: Math.abs(y2 - draftBox.y)
    });
  };

  const finishDraw = () => {
    if (drawing && draftBox && draftBox.width > 0.01 && draftBox.height > 0.01) {
      onAddBBox(media.label, draftBox, currentTime);
    }
    setDrawing(false);
    setDraftBox(null);
  };

  return (
    <article className="media-card">
      <div className="media-card-head">
        <div>
          <h3>{title}</h3>
          <small>{media?.path || "no path"}</small>
        </div>
        <span className={media?.exists ? "media-ok" : "media-missing"}>
          {media?.exists ? "media ok" : "media missing"}
        </span>
      </div>
      <div
        className={`media-frame ${isDrawMode ? "draw-mode" : ""}`}
        ref={frameRef}
        onMouseDown={startDraw}
        onMouseMove={moveDraw}
        onMouseUp={finishDraw}
        onMouseLeave={finishDraw}
      >
        {media?.exists && media.kind === "video" && (
          <video
            ref={mediaRef}
            controls
            src={media.url}
            onTimeUpdate={(event) => setCurrentTime(event.currentTarget.currentTime)}
          />
        )}
        {media?.exists && media.kind === "audio" && (
          <div className="audio-frame">
            <audio
              ref={mediaRef}
              controls
              src={media.url}
              onTimeUpdate={(event) => setCurrentTime(event.currentTarget.currentTime)}
            />
          </div>
        )}
        {media?.exists && media.kind === "image" && <img src={media.url} alt={title} />}
        {!media?.exists && (
          <div className="missing-frame">
            <strong>媒体未挂载</strong>
            <span>仍可审核字段；需要播放时配置 ANNOTATION_MEDIA_MAP。</span>
          </div>
        )}
        {mediaBBoxes.map((box, index) => (
          <div
            key={`${box.media}-${index}`}
            className="bbox"
            style={{
              left: `${box.x * 100}%`,
              top: `${box.y * 100}%`,
              width: `${box.width * 100}%`,
              height: `${box.height * 100}%`
            }}
          />
        ))}
        {draftBox && (
          <div
            className="bbox draft"
            style={{
              left: `${draftBox.x * 100}%`,
              top: `${draftBox.y * 100}%`,
              width: `${draftBox.width * 100}%`,
              height: `${draftBox.height * 100}%`
            }}
          />
        )}
      </div>
      <div className="media-tools">
        <span>time {currentTime.toFixed(2)}s</span>
        <button type="button" onClick={() => onAddTimeSpan("audio", currentTime)}>取音频段</button>
        <button type="button" onClick={() => onAddTimeSpan("video", currentTime)}>取视频段</button>
        <button
          type="button"
          className={isDrawMode ? "active" : ""}
          onClick={() => setIsDrawMode((value) => !value)}
          disabled={media?.kind === "audio"}
        >
          框选区域
        </button>
      </div>
    </article>
  );
}

function EvidenceList({ annotation }) {
  const spans = annotation.recovery_evidence?.annotation_app_time_spans || [];
  const boxes = annotation.defect_location?.bboxes || [];
  return (
    <div className="evidence-strip">
      <div>
        <strong>时间证据</strong>
        {spans.length === 0 && <span>暂无</span>}
        {spans.map((span, index) => (
          <span key={`${span.modality}-${index}`}>{span.modality}: {span.start.toFixed(2)}-{span.end.toFixed(2)}s</span>
        ))}
      </div>
      <div>
        <strong>框选</strong>
        {boxes.length === 0 && <span>暂无</span>}
        {boxes.map((box, index) => (
          <span key={`${box.media}-${index}`}>{box.media}: {(box.width * 100).toFixed(1)}% x {(box.height * 100).toFixed(1)}%</span>
        ))}
      </div>
    </div>
  );
}

function AnnotationForm({ annotation, options, onChange, onWholeChange }) {
  if (!annotation) {
    return <aside className="form-panel empty">选择实例后显示 v1 标注字段。</aside>;
  }

  const setRouteList = (path, route) => {
    const next = structuredClone(annotation);
    let cursor = next;
    for (let index = 0; index < path.length - 1; index += 1) {
      cursor[path[index]] = cursor[path[index]] || {};
      cursor = cursor[path[index]];
    }
    const key = path[path.length - 1];
    const current = Array.isArray(cursor[key]) ? cursor[key] : [];
    const exists = current.some((item) => JSON.stringify(item) === JSON.stringify(route));
    cursor[key] = exists ? current.filter((item) => JSON.stringify(item) !== JSON.stringify(route)) : [...current, route];
    onWholeChange(next);
  };

  return (
    <aside className="form-panel">
      <div className="panel-header sticky">
        <div>
          <h2>v1 标注字段</h2>
          <span>{annotation.instance_id}</span>
        </div>
        <SelectField
          label="状态"
          value={annotation.review_status}
          options={options.review_status}
          onChange={(value) => onChange(["review_status"], value)}
        />
      </div>

      <FieldGroup title="Source screening">
        <SelectField
          label="仅看题目是否可答"
          value={annotation.question_only_blind?.answerable_without_media}
          options={options.answerable_without_media}
          onChange={(value) => onChange(["question_only_blind", "answerable_without_media"], value)}
        />
        <SelectField
          label="blind confidence"
          value={annotation.question_only_blind?.blind_confidence}
          options={options.blind_confidence}
          onChange={(value) => onChange(["question_only_blind", "blind_confidence"], value)}
        />
        <TextField
          label="blind answer"
          value={annotation.question_only_blind?.blind_answer || ""}
          onChange={(value) => onChange(["question_only_blind", "blind_answer"], value)}
        />
        <TwoColumn>
          <SelectField
            label="source audio"
            value={annotation.source_modality_necessity?.audio}
            options={options.source_modality}
            onChange={(value) => onChange(["source_modality_necessity", "audio"], value)}
          />
          <SelectField
            label="source video"
            value={annotation.source_modality_necessity?.video}
            options={options.source_modality}
            onChange={(value) => onChange(["source_modality_necessity", "video"], value)}
          />
        </TwoColumn>
        <SelectField
          label="joint required"
          value={annotation.source_modality_necessity?.audio_video_joint_required}
          options={options.audio_video_joint_required}
          onChange={(value) => onChange(["source_modality_necessity", "audio_video_joint_required"], value)}
        />
        <TextAreaField
          label="source evidence note"
          value={annotation.source_evidence_note || ""}
          onChange={(value) => onChange(["source_evidence_note"], value)}
        />
      </FieldGroup>

      <FieldGroup title="Corrupted instance">
        <TwoColumn>
          <SelectField
            label="audio quality"
            value={annotation.modality_quality_status?.audio}
            options={options.modality_quality}
            onChange={(value) => onChange(["modality_quality_status", "audio"], value)}
          />
          <SelectField
            label="video quality"
            value={annotation.modality_quality_status?.video}
            options={options.modality_quality}
            onChange={(value) => onChange(["modality_quality_status", "video"], value)}
          />
        </TwoColumn>
        <TwoColumn>
          <SelectField
            label="audio relevance"
            value={annotation.modality_task_relevance?.audio}
            options={options.modality_task_relevance}
            onChange={(value) => onChange(["modality_task_relevance", "audio"], value)}
          />
          <SelectField
            label="video relevance"
            value={annotation.modality_task_relevance?.video}
            options={options.modality_task_relevance}
            onChange={(value) => onChange(["modality_task_relevance", "video"], value)}
          />
        </TwoColumn>
        <SelectField
          label="cross-modal relation"
          value={annotation.cross_modal_relation}
          options={options.cross_modal_relation}
          onChange={(value) => onChange(["cross_modal_relation"], value)}
        />
        <SelectField
          label="corruption relevance"
          value={annotation.corruption_relevance}
          options={options.corruption_relevance}
          onChange={(value) => onChange(["corruption_relevance"], value)}
        />
        <SelectField
          label="corruption effect"
          value={annotation.corruption_effect}
          options={options.corruption_effect}
          onChange={(value) => onChange(["corruption_effect"], value)}
        />
      </FieldGroup>

      <FieldGroup title="Answerability and recovery">
        <SelectField
          label="post-corruption answerability"
          value={annotation.post_corruption_answerability}
          options={options.post_corruption_answerability}
          onChange={(value) => onChange(["post_corruption_answerability"], value)}
        />
        <SelectField
          label="cross-modal recoverability"
          value={annotation.cross_modal_recoverability}
          options={options.cross_modal_recoverability}
          onChange={(value) => onChange(["cross_modal_recoverability"], value)}
        />
        <SelectField
          label="main answerability"
          value={annotation.main_answerability}
          options={options.main_answerability}
          onChange={(value) => onChange(["main_answerability"], value)}
        />
        <CheckboxGroup
          label="recovery source"
          values={annotation.recovery_source || []}
          options={["audio", "video"]}
          onChange={(values) => onChange(["recovery_source"], values)}
        />
        <TextAreaField
          label="recovery note"
          value={annotation.recovery_evidence?.note || ""}
          onChange={(value) => onChange(["recovery_evidence", "note"], value)}
        />
      </FieldGroup>

      <FieldGroup title="Oracle policy action">
        <RouteButtons
          label="acceptable routes"
          routes={annotation.oracle_policy_action?.acceptable_routes || []}
          onToggle={(route) => setRouteList(["oracle_policy_action", "acceptable_routes"], route)}
        />
        <CheckboxGroup
          label="preferred route"
          values={annotation.oracle_policy_action?.preferred_route || []}
          options={["audio", "video"]}
          onChange={(values) => onChange(["oracle_policy_action", "preferred_route"], values)}
        />
        <RouteButtons
          label="disallowed routes"
          routes={annotation.oracle_policy_action?.disallowed_routes || []}
          onToggle={(route) => setRouteList(["oracle_policy_action", "disallowed_routes"], route)}
        />
        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={Boolean(annotation.oracle_policy_action?.abstain)}
            onChange={(event) => onChange(["oracle_policy_action", "abstain"], event.target.checked)}
          />
          oracle abstain
        </label>
        <SelectField
          label="oracle answerability"
          value={annotation.oracle_policy_action?.answerability}
          options={options.oracle_answerability}
          onChange={(value) => onChange(["oracle_policy_action", "answerability"], value)}
        />
        <TextField
          label="expected answer"
          value={annotation.oracle_policy_action?.expected_answer || ""}
          onChange={(value) => onChange(["oracle_policy_action", "expected_answer"], value || null)}
        />
        <SelectField
          label="risk level"
          value={annotation.oracle_policy_action?.risk_level}
          options={options.oracle_risk_level}
          onChange={(value) => onChange(["oracle_policy_action", "risk_level"], value)}
        />
      </FieldGroup>

      <FieldGroup title="QC notes">
        <SelectField
          label="annotation confidence"
          value={annotation.annotation_confidence}
          options={options.annotation_confidence}
          onChange={(value) => onChange(["annotation_confidence"], value)}
        />
        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={Boolean(annotation.risk_sensitive)}
            onChange={(event) => onChange(["risk_sensitive"], event.target.checked)}
          />
          risk-sensitive / exclude unless adjudicated
        </label>
        <TextAreaField
          label="annotator notes"
          value={annotation.annotator_notes || ""}
          onChange={(value) => onChange(["annotator_notes"], value)}
        />
      </FieldGroup>
    </aside>
  );
}

function FieldGroup({ title, children }) {
  return (
    <section className="field-group">
      <h3>{title}</h3>
      {children}
    </section>
  );
}

function TwoColumn({ children }) {
  return <div className="two-column">{children}</div>;
}

function SelectField({ label, value, options = [], onChange }) {
  return (
    <label className="field">
      <span>{label}</span>
      <select value={value || ""} onChange={(event) => onChange(event.target.value)}>
        <option value="">unset</option>
        {(options || []).map((option) => (
          <option key={option} value={option}>{option}</option>
        ))}
      </select>
    </label>
  );
}

function TextField({ label, value, onChange }) {
  return (
    <label className="field">
      <span>{label}</span>
      <input value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function TextAreaField({ label, value, onChange }) {
  return (
    <label className="field">
      <span>{label}</span>
      <textarea value={value} onChange={(event) => onChange(event.target.value)} rows={3} />
    </label>
  );
}

function CheckboxGroup({ label, values = [], options = [], onChange }) {
  const toggle = (option) => {
    const next = values.includes(option)
      ? values.filter((item) => item !== option)
      : [...values, option];
    onChange(next);
  };

  return (
    <div className="field">
      <span>{label}</span>
      <div className="toggle-row">
        {options.map((option) => (
          <button
            type="button"
            key={option}
            className={values.includes(option) ? "active" : ""}
            onClick={() => toggle(option)}
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  );
}

function RouteButtons({ label, routes, onToggle }) {
  const routeOptions = [["audio"], ["video"], ["audio", "video"]];
  return (
    <div className="field">
      <span>{label}</span>
      <div className="toggle-row">
        {routeOptions.map((route) => {
          const active = routes.some((item) => JSON.stringify(item) === JSON.stringify(route));
          return (
            <button type="button" key={routeLabel(route)} className={active ? "active" : ""} onClick={() => onToggle(route)}>
              {routeLabel(route)}
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default App;
