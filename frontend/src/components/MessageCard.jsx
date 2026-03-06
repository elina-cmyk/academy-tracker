import React, { useRef, useEffect } from "react";

function fmtDate(d) {
  const dt = new Date(d + "T00:00:00");
  return dt.toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
    weekday: "short",
  });
}

export function MessageCard({ msg, isLatest, onToggleHw, onDelete, scrollToMe }) {
  const ref = useRef(null);

  useEffect(() => {
    if (scrollToMe && ref.current) {
      ref.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [scrollToMe]);

  return (
    <div ref={ref} className={`msg-card ${isLatest ? "latest" : ""}`}>
      <div
        className="msg-accent-bar"
        style={{ background: msg.subject_color || "#888" }}
      />
      <div className="msg-header">
        <div className="msg-meta">
          <span className="msg-time">{msg.time}</span>
          {isLatest && <span className="msg-latest-badge">최신</span>}
          {msg.academy && (
            <span className="msg-academy">🏫 {msg.academy}</span>
          )}
        </div>
        <button
          className="btn-del"
          onClick={() => onDelete(msg.id)}
          title="삭제"
        >
          ✕
        </button>
      </div>

      <div className="msg-body">{msg.content}</div>

      <div className="msg-footer">
        <div
          className={`hw-check ${msg.hw_done ? "done" : ""}`}
          onClick={() => onToggleHw(msg.id, !msg.hw_done)}
        >
          <div className="hw-checkbox" />
          숙제 완료
        </div>
        {msg.score && (
          <div className="msg-score">
            <span className="score-badge">🏆 {msg.score}</span>
          </div>
        )}
      </div>
    </div>
  );
}

export function DateGroup({ date, messages, latestId, onToggleHw, onDelete }) {
  return (
    <div className="date-group">
      <div className="date-label">{fmtDate(date)}</div>
      {messages.map((msg) => (
        <MessageCard
          key={msg.id}
          msg={msg}
          isLatest={msg.id === latestId}
          scrollToMe={msg.id === latestId}
          onToggleHw={onToggleHw}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
