import type { Task, TaskFields } from '../types';

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`/api/tasks${path}`, {
      ...options, headers: { 'Content-Type': 'application/json' },
      signal: options.signal ?? AbortSignal.timeout(15000),
    });
  } catch {
    throw new Error('Unable to reach LifeDesk. Your input is still here. If you were saving, refresh the list before retrying to check whether it was saved.');
  }
  if (!response.ok) {
    if (response.status === 404) throw new Error('This task no longer exists. Refresh the list to see the latest tasks.');
    if (response.status === 422) throw new Error('Please check the title, date, and priority, then try again.');
    throw new Error('LifeDesk could not finish the request. Please try again.');
  }
  return response.status === 204 ? undefined as T : response.json() as Promise<T>;
}
export const listTasks = (signal?: AbortSignal) => request<Task[]>('', { signal });
export const createTask = (fields: TaskFields) => request<Task>('', { method: 'POST', body: JSON.stringify(fields) });
export const updateTask = (id: number, fields: Partial<TaskFields> & { is_completed?: boolean }) =>
  request<Task>(`/${id}`, { method: 'PATCH', body: JSON.stringify(fields) });
export const deleteTask = (id: number) => request<void>(`/${id}`, { method: 'DELETE' });
