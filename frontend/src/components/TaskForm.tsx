import { useId, useRef, useState } from 'react';
import type { FormEvent } from 'react';
import type { Priority, Task, TaskFields } from '../types';

interface Props {
  task?: Task;
  onSave: (fields: TaskFields) => Promise<void>;
  onCancel?: () => void;
  disabled?: boolean;
}
export default function TaskForm({ task, onSave, onCancel, disabled = false }: Props) {
  const id = useId();
  const [title, setTitle] = useState(task?.title ?? '');
  const [description, setDescription] = useState(task?.description ?? '');
  const [dueDate, setDueDate] = useState(task?.due_date ?? '');
  const [priority, setPriority] = useState<Priority>(task?.priority ?? 'medium');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const inFlight = useRef(false);
  const titleInput = useRef<HTMLInputElement>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (inFlight.current || disabled) return;
    if (!title.trim()) {
      setError('Please enter a title that is not blank.');
      titleInput.current?.focus(); return;
    }
    inFlight.current = true; setSaving(true); setError('');
    try {
      await onSave({ title: title.trim(), description: description || null, due_date: dueDate || null, priority });
      if (!task) {
        setTitle(''); setDescription(''); setDueDate(''); setPriority('medium');
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Could not save. Please try again.');
    } finally { inFlight.current = false; setSaving(false); }
  }
  return <form onSubmit={submit} aria-label={task ? 'Edit task' : 'Create task'} aria-busy={saving}>
    <fieldset disabled={saving || disabled}>
      <legend>{task ? 'Edit task' : 'Add a task'}</legend>
      <label htmlFor={`${id}-title`}>Title <span className="hint">(required)</span></label>
      <input ref={titleInput} id={`${id}-title`} value={title} onChange={(e) => setTitle(e.target.value)} maxLength={200} required placeholder="What would you like to do?" />
      <label htmlFor={`${id}-description`}>Description <span className="hint">(optional)</span></label>
      <textarea id={`${id}-description`} value={description} onChange={(e) => setDescription(e.target.value)} rows={3} placeholder="A few details to help you get started" />
      <div className="form-row">
        <div><label htmlFor={`${id}-date`}>Due date <span className="hint">(optional)</span></label>
          <input id={`${id}-date`} type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} /></div>
        <div><label htmlFor={`${id}-priority`}>Priority</label>
          <select id={`${id}-priority`} value={priority} onChange={(e) => setPriority(e.target.value as Priority)}>
            <option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option>
          </select></div>
      </div>
      <div className="actions"><button type="submit">{saving ? 'Saving…' : task ? 'Save changes' : 'Add task'}</button>
        {onCancel && <button className="secondary" type="button" onClick={onCancel}>Cancel</button>}</div>
    </fieldset>
    {error && <p className="error" role="alert">{error}</p>}
  </form>;
}
