import TaskDashboard from './components/TaskDashboard';

export default function App() {
  return (
    <main className="shell">
      <header>
        <a className="brand" href="/" aria-label="LifeDesk home">LifeDesk</a>
        <span className="version">A little space for your day</span>
      </header>
      <section className="welcome">
        <p className="eyebrow">YOUR DAILY DESK</p>
        <h1>Make room for what matters.</h1>
        <p className="intro">One place to capture your tasks and take the next step.</p>
      </section>
      <TaskDashboard />
      <footer>LifeDesk · Your personal daily desk</footer>
    </main>
  );
}
