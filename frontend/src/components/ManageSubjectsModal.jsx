import React, { useState } from "react";

const PALETTE = ["#7c6af7","#f76a8a","#6af7c8","#f7c46a","#6ab8f7","#f7a06a","#a0f76a","#f76af7"];

export default function ManageSubjectsModal({ subjects, onSave, onClose }) {
  const [list, setList] = useState(subjects.map((s) => ({ ...s })));

  const update = (i, key, val) =>
    setList((l) => l.map((s, idx) => (idx === i ? { ...s, [key]: val } : s)));

  const add = () =>
    setList((l) => [
      ...l,
      { id: null, name: "새 과목", color: PALETTE[l.length % PALETTE.length] },
    ]);

  const remove = (i) => {
    if (list.length <= 1) { alert("과목은 최소 1개 필요해요."); return; }
    setList((l) => l.filter((_, idx) => idx !== i));
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal manage-modal" onClick={(e) => e.stopPropagation()}>
        <h3>⚙ 과목 관리</h3>

        <div className="subject-list-manage">
          {list.map((s, i) => (
            <div key={i} className="subject-item-manage">
              <input
                type="color"
                className="color-picker"
                value={s.color}
                onChange={(e) => update(i, "color", e.target.value)}
              />
              <input
                type="text"
                className="subject-name-input"
                value={s.name}
                placeholder="과목명"
                onChange={(e) => update(i, "name", e.target.value)}
              />
              <button className="btn-remove-subject" onClick={() => remove(i)}>
                ✕
              </button>
            </div>
          ))}
        </div>

        <button className="btn-add-subject" onClick={add}>
          ＋ 과목 추가
        </button>

        <div className="modal-btns">
          <button className="btn-cancel" onClick={onClose}>
            취소
          </button>
          <button className="btn-save" onClick={() => onSave(list)}>
            저장
          </button>
        </div>
      </div>
    </div>
  );
}
