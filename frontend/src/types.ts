export type Priority = 'low' | 'medium' | 'high';
export interface TaskFields {
  title: string;
  description: string | null;
  due_date: string | null;
  priority: Priority;
}
export interface Task extends TaskFields {
  id: number;
  is_completed: boolean;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}
