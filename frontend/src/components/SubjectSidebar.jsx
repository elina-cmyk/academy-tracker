import React from "react";

export default function SubjectSidebar({ subjects, current, counts, onSelect, onManage }) {
  return (
    <nav className="sidebar">
      <div className="sidebar-section">과목</div>

      <button
        className={`subject-btn ${current === "all" ? "active" : ""}`}
        onClick={() => onSelect("all")}
      >
        <span className="subject-dot" style={{ background: "#888" }} />
        전체
        {counts.all > 0 && <span className="subject-count">{counts.all}</span>}
      </button>

      {subjects.map((s) => (
        <button
          key={s.id}
          className={`subject-btn ${current === s.id ? "active" : ""}`}
          onClick={() => onSelect(s.id)}
        >
          <span className="subject-dot" style={{ background: s.color }} />
          {s.name}
          {counts[s.id] > 0 && <span className="subject-count">{counts[s.id]}</span>}
        </button>
      ))}

      <div style={{ marginTop: "auto", padding: "12px" }}>
        <button className="btn-manage" onClick={onManage}>
          ⚙ 과목 관리
        </button>
      </div>
    </nav>
  );
}
