import { useEffect, useState } from 'react';
import { checkHealth } from './api/client';

type Connection = 'checking' | 'connected' | 'unavailable';

export default function App() {
  const [connection, setConnection] = useState<Connection>('checking');
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 8000);
    let active = true;

    checkHealth(controller.signal)
      .then(() => {
        if (active) setConnection('connected');
      })
      .catch(() => {
        if (active) setConnection('unavailable');
      })
      .finally(() => window.clearTimeout(timeout));

    return () => {
      active = false;
      window.clearTimeout(timeout);
      controller.abort();
    };
  }, [attempt]);

  return (
    <main className="shell">
      <header>
        <a className="brand" href="/" aria-label="LifeDesk home">LifeDesk</a>
        <span className="version">A little space for your day</span>
      </header>

      <section className="welcome" aria-labelledby="welcome-title">
        <p className="eyebrow">YOUR DAILY DESK</p>
        <h1 id="welcome-title">Make room for what matters.</h1>
        <p className="intro">Welcome to LifeDesk, your personal daily productivity dashboard.</p>

        <div className="connection-card">
          <div>
            <h2>Getting started</h2>
            <p>The foundation is ready. Tasks and quick notes will follow in the next milestones.</p>
          </div>
          <p className={`status ${connection}`} role="status" aria-live="polite">
            <span className="status-dot" aria-hidden="true" />
            {connection === 'checking' && 'Checking connection…'}
            {connection === 'connected' && 'Connected to LifeDesk'}
            {connection === 'unavailable' && 'Unable to connect. Please try again.'}
          </p>
          {connection === 'unavailable' && (
            <button type="button" onClick={() => {
              setConnection('checking');
              setAttempt((value) => value + 1);
            }}>Try again</button>
          )}
        </div>
      </section>
      <footer>LifeDesk · Project foundation</footer>
    </main>
  );
}
