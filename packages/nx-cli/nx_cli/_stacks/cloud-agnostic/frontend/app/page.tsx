import { getApiUrl } from '../lib/api';

export default function Home() {
  const api = getApiUrl();
  return (
    <main className="container">
      <h1>{{project_title}}</h1>
      <p>Cloud-agnostic foundation — backend + frontend + Supabase, all via Docker.</p>
      <ul>
        <li>Backend API: <a href={api}>{api}</a></li>
        <li>Health: <a href={api + '/health'}>{api}/health</a></li>
        <li>API docs: <a href={api + '/docs'}>{api}/docs</a></li>
      </ul>
      <p>Add your business logic on top — the foundation is ready.</p>
    </main>
  );
}
