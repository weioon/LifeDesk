import { useEffect, useRef, useState } from 'react';
import * as api from '../api/tasks';
import type { Task } from '../types';
import TaskForm from './TaskForm';
import TaskList from './TaskList';

export default function TaskDashboard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [attempt, setAttempt] = useState(0);
  const revision = useRef(0);
  useEffect(() => {
    const controller = new AbortController();
    const currentRevision = revision.current;
    const timeout = window.setTimeout(() => controller.abort(), 15000);
    let active = true;
    api.listTasks(controller.signal).then((items) => {
      if (active && revision.current === currentRevision) { setTasks(items); setLoaded(true); }
    }).catch(() => {
      if (active) setError('Unable to load tasks. Make sure LifeDesk is running, then try again.');
    }).finally(() => { window.clearTimeout(timeout); if (active) setLoading(false); });
    return () => { active = false; controller.abort(); window.clearTimeout(timeout); };
  }, [attempt]);
  function saved(task: Task) {
    revision.current += 1;
    setTasks((items) => items.some((item) => item.id === task.id)
      ? items.map((item) => item.id === task.id ? task : item) : [...items, task]);
    setNotice('Task saved.');
  }
  return <section className="dashboard" aria-label="Task dashboard">
    <aside className="form-panel"><TaskForm disabled={loading} onSave={async (fields) => saved(await api.createTask(fields))} /></aside>
    <div className="tasks-panel">
      <div className="list-toolbar"><p className="hint">A little progress, every day.</p>
        <button className="secondary" disabled={loading} onClick={() => { setLoading(true); setError(''); setNotice(''); setAttempt((value) => value + 1); }}>Refresh list</button></div>
      <p className="notice" role="status">{loading ? 'Loading tasks…' : notice}</p>
      {error && <p className="error" role="alert">{error}</p>}
      {loaded && <TaskList tasks={tasks} onSaved={saved} onDeleted={(id) => {
        revision.current += 1; setTasks((items) => items.filter((task) => task.id !== id)); setNotice('Task deleted.');
      }} />}
    </div>
  </section>;
}
