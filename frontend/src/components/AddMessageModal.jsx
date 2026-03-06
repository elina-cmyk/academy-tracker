import React, { useState, useEffect } from "react";

function today() {
  return new Date().toISOString().slice(0, 10);
}

export default function AddMessageModal({ subjects, defaultSubjectId, onSave, onClose }) {
  const [form, setForm] = useState({
    subject_id: defaultSubjectId || subjects[0]?.id || "",
    date: today(),
    academy: "",
    content: "",
    score: "",
  });

  useEffect(() => {
    if (defaultSubjectId) setForm((f) => ({ ...f, subject_id: defaultSubjectId }));
  }, [defaultSubjectId]);

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const handleSave = () => {
    if (!form.content.trim()) {
      alert("문자 내용을 입력해주세요.");
      return;
    }
    onSave({
      subject_id: form.subject_id,
      date: form.date,
      academy: form.academy.trim() || null,
      content: form.content.trim(),
      score: form.score.trim() || null,
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h3>📩 학원 문자 추가</h3>

        <div className="tip-box">
          <strong>💡 사용 방법</strong>
          <br />
          학원에서 온 문자를 <strong>복사(길게 누르기 → 복사)</strong> 후
          <br />
          아래 내용란에 붙여넣기 하세요!
        </div>

        <div className="form-row">
          <label>과목 선택</label>
          <select value={form.subject_id} onChange={(e) => set("subject_id", e.target.value)}>
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>

        <div className="form-row">
          <label>날짜</label>
          <input
            type="date"
            value={form.date}
            onChange={(e) => set("date", e.target.value)}
          />
        </div>

        <div className="form-row">
          <label>학원명 (선택)</label>
          <input
            type="text"
            placeholder="예: 수학의정석, 강남영어학원"
            value={form.academy}
            onChange={(e) => set("academy", e.target.value)}
          />
        </div>

        <div className="form-row">
          <label>문자 내용 붙여넣기</label>
          <textarea
            placeholder="학원에서 온 문자 내용을 그대로 붙여넣으세요..."
            value={form.content}
            onChange={(e) => set("content", e.target.value)}
          />
        </div>

        <div className="form-row">
          <label>성적/점수 (선택)</label>
          <input
            type="text"
            placeholder="예: 95점, A+, 반 3등"
            value={form.score}
            onChange={(e) => set("score", e.target.value)}
          />
        </div>

        <div className="modal-btns">
          <button className="btn-cancel" onClick={onClose}>
            취소
          </button>
          <button className="btn-save" onClick={handleSave}>
            저장
          </button>
        </div>
      </div>
    </div>
  );
}
