import React, { useState, useEffect, useCallback } from "react";
import { api } from "./api/client";
import SubjectSidebar from "./components/SubjectSidebar";
import { DateGroup } from "./components/MessageCard";
import AddMessageModal from "./components/AddMessageModal";
import ManageSubjectsModal from "./components/ManageSubjectsModal";
import "./App.css";

export default function App() {
  const [subjects, setSubjects] = useState([]);
  const [messages, setMessages] = useState([]);
  const [currentSubject, setCurrentSubject] = useState("all");
  const [showAdd, setShowAdd] = useState(false);
  const [showManage, setShowManage] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ── Load data ──────────────────────────────────────
  const loadAll = useCallback(async () => {
    try {
      const [subs, msgs] = await Promise.all([api.getSubjects(), api.getMessages()]);
      setSubjects(subs);
      setMessages(msgs);
      setError(null);
    } catch (e) {
      setError("서버에 연결할 수 없어요. 백엔드가 실행 중인지 확인해주세요.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadAll(); }, [loadAll]);

  // ── Filtered + grouped messages ────────────────────
  const filtered =
    currentSubject === "all"
      ? messages
      : messages.filter((m) => m.subject_id === currentSubject);

  const byDate = filtered.reduce((acc, m) => {
    acc[m.date] = acc[m.date] || [];
    acc[m.date].push(m);
    return acc;
  }, {});

  const sortedDates = Object.keys(byDate).sort((a, b) => b.localeCompare(a));
  const latestId = filtered.length > 0 ? filtered[0].id : null;

  // ── Counts ────────────────────────────────────────
  const counts = { all: messages.length };
  subjects.forEach((s) => {
    counts[s.id] = messages.filter((m) => m.subject_id === s.id).length;
  });

  // ── Handlers ─────────────────────────────────────
  const handleSubjectSelect = (id) => setCurrentSubject(id);

  const handleAddMessage = async (data) => {
    try {
      const msg = await api.createMessage(data);
      setMessages((prev) => [msg, ...prev]);
      setShowAdd(false);
    } catch (e) {
      alert("저장 실패: " + e.message);
    }
  };

  const handleToggleHw = async (id, done) => {
    try {
      const updated = await api.updateMessage(id, { hw_done: done });
      setMessages((prev) => prev.map((m) => (m.id === id ? updated : m)));
    } catch (e) {
      alert("업데이트 실패");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("이 문자를 삭제할까요?")) return;
    try {
      await api.deleteMessage(id);
      setMessages((prev) => prev.filter((m) => m.id !== id));
    } catch (e) {
      alert("삭제 실패");
    }
  };

  const handleSaveSubjects = async (list) => {
    try {
      // New subjects (id === null)
      const creates = list.filter((s) => !s.id);
      const updates = list.filter((s) => s.id);
      const delIds = subjects.filter((s) => !list.find((l) => l.id === s.id)).map((s) => s.id);

      await Promise.all(delIds.map((id) => api.deleteSubject(id)));
      await Promise.all(updates.map((s) => api.updateSubject(s.id, { name: s.name, color: s.color })));
      await Promise.all(creates.map((s) => api.createSubject({ name: s.name, color: s.color })));

      await loadAll();
      setShowManage(false);
      setCurrentSubject("all");
    } catch (e) {
      alert("저장 실패: " + e.message);
    }
  };

  // ── Current subject info ───────────────────────────
  const currentSubjectInfo = subjects.find((s) => s.id === currentSubject);

  // ── Render ────────────────────────────────────────
  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner" />
        <p>불러오는 중...</p>
      </div>
    );
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <h1>📚 학원 알림장</h1>
        <div className="header-actions">
          <button className="btn-icon" onClick={() => setShowManage(true)}>
            ⚙ 과목 관리
          </button>
          <button className="btn-icon btn-icon-primary" onClick={() => setShowAdd(true)}>
            + 문자 추가
          </button>
        </div>
      </header>

      {error && (
        <div className="error-bar">
          ⚠ {error}
          <button onClick={loadAll}>재시도</button>
        </div>
      )}

      <div className="layout">
        <SubjectSidebar
          subjects={subjects}
          current={currentSubject}
          counts={counts}
          onSelect={handleSubjectSelect}
          onManage={() => setShowManage(true)}
        />

        <main className="main">
          <div className="main-top">
            <div className="main-title">
              <div
                className="title-dot"
                style={{ background: currentSubjectInfo?.color || "#888" }}
              />
              <h2>{currentSubjectInfo?.name || "전체"}</h2>
              <span className="main-count">{filtered.length}건</span>
            </div>
            <button className="btn-add" onClick={() => setShowAdd(true)}>
              ＋ 문자 추가
            </button>
          </div>

          <div className="messages-container">
            {sortedDates.length === 0 ? (
              <div className="empty">
                <div className="empty-icon">💬</div>
                <p>아직 추가된 학원 문자가 없어요</p>
                <p>
                  <strong>'+ 문자 추가'</strong>를 눌러 시작하세요
                </p>
              </div>
            ) : (
              sortedDates.map((date) => (
                <DateGroup
                  key={date}
                  date={date}
                  messages={byDate[date]}
                  latestId={latestId}
                  onToggleHw={handleToggleHw}
                  onDelete={handleDelete}
                />
              ))
            )}
          </div>
        </main>
      </div>

      {showAdd && (
        <AddMessageModal
          subjects={subjects}
          defaultSubjectId={currentSubject !== "all" ? currentSubject : null}
          onSave={handleAddMessage}
          onClose={() => setShowAdd(false)}
        />
      )}

      {showManage && (
        <ManageSubjectsModal
          subjects={subjects}
          onSave={handleSaveSubjects}
          onClose={() => setShowManage(false)}
        />
      )}
    </div>
  );
}
