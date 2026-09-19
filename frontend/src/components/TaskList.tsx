import type { Task } from '../types';
import TaskItem from './TaskItem';
interface Props { tasks: Task[]; onSaved: (task: Task) => void; onDeleted: (id: number) => void; }
export default function TaskList({ tasks, onSaved, onDeleted }: Props) {
  const active = tasks.filter((task) => !task.is_completed);
  const completed = tasks.filter((task) => task.is_completed);
  const render = (items: Task[]) => <ul className="task-list">{items.map((task) => <TaskItem key={task.id} task={task} onSaved={onSaved} onDeleted={onDeleted} />)}</ul>;
  return <>
    <h2>Active tasks <span className="count">{active.length}</span></h2>
    {active.length ? render(active) : <p className="empty">Nothing on your list. Add a task when you’re ready.</p>}
    <details className="completed-section">
      <summary>Finished tasks ({completed.length})</summary>
      <p className="hint">You can reopen a task whenever you need to.</p>
      {completed.length ? render(completed) : <p className="empty">No finished tasks yet.</p>}
    </details>
  </>;
}
