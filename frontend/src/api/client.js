const BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

async function req(method, path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(await res.text());
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  // Subjects
  getSubjects: () => req("GET", "/subjects"),
  createSubject: (data) => req("POST", "/subjects", data),
  updateSubject: (id, data) => req("PUT", `/subjects/${id}`, data),
  deleteSubject: (id) => req("DELETE", `/subjects/${id}`),

  // Messages
  getMessages: (subjectId) =>
    req("GET", subjectId ? `/messages?subject_id=${subjectId}` : "/messages"),
  createMessage: (data) => req("POST", "/messages", data),
  updateMessage: (id, data) => req("PATCH", `/messages/${id}`, data),
  deleteMessage: (id) => req("DELETE", `/messages/${id}`),
};
