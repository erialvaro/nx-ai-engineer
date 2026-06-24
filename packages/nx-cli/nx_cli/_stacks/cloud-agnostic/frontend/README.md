# Frontend — {{project_title}}

Next.js (App Router, TypeScript), built with `output: standalone` so the
production image is small and runs on any Docker host (cloud-agnostic). It talks
to the backend only through `NEXT_PUBLIC_API_URL`.

## Run

```bash
# via Docker (recommended): from the project root
make up
# or locally:
npm install
npm run dev          # http://localhost:3000
```

## Layout

```
app/layout.tsx   # root layout + metadata
app/page.tsx     # landing page (links to backend health/docs)
lib/api.ts       # backend access via env (no provider SDK)
```
