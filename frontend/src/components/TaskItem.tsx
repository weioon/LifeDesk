import { useRef, useState } from 'react';
import * as api from '../api/tasks';
import type { Task } from '../types';
import TaskForm from './TaskForm';

interface Props { task: Task; onSaved: (task: Task) => void; onDeleted: (id: number) => void; }
export default function TaskItem({ task, onSaved, onDeleted }: Props) {
  const [editing, setEditing] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const inFlight = useRef(false);

  async function act(remove: boolean) {
    if (inFlight.current) return;
    inFlight.current = true; setBusy(true); setError('');
    try {
      if (remove) { await api.deleteTask(task.id); onDeleted(task.id); }
      else onSaved(await api.updateTask(task.id, { is_completed: !task.is_completed }));
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Could not update task. Please try again.');
    } finally { inFlight.current = false; setBusy(false); }
  }
  return <li className={`task-card ${task.is_completed ? 'completed' : ''}`}>
    {editing ? <TaskForm task={task} onCancel={() => setEditing(false)} onSave={async (fields) => {
      const saved = await api.updateTask(task.id, fields); onSaved(saved); setEditing(false);
    }} /> : <>
      <div className="task-heading"><h3>{task.title}</h3><span className={`priority ${task.priority}`}>{task.priority} priority</span></div>
      {task.description && <p className="description">{task.description}</p>}
      <p className="task-date">{task.due_date ? <>Due <time dateTime={task.due_date}>{new Date(`${task.due_date}T12:00:00`).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}</time></> : 'No due date'}</p>
      {confirming ? <div className="delete-confirm" role="group" aria-label="Confirm deletion">
        <p>Delete “{task.title}”? This cannot be undone.</p>
        <div className="actions"><button className="danger" disabled={busy} onClick={() => void act(true)}>{busy ? 'Deleting…' : 'Confirm delete'}</button>
          <button className="secondary" disabled={busy} onClick={() => setConfirming(false)}>Keep task</button></div>
      </div> : <div className="actions">
        <button disabled={busy} onClick={() => void act(false)}>{busy ? 'Saving…' : task.is_completed ? 'Reopen' : 'Mark complete'}</button>
        <button className="secondary" disabled={busy} onClick={() => { setError(''); setEditing(true); }}>Edit</button>
        <button className="text-danger" disabled={busy} onClick={() => { setError(''); setConfirming(true); }}>Delete</button>
      </div>}
      {error && <p className="error" role="alert">{error}</p>}
    </>}
  </li>;
}
