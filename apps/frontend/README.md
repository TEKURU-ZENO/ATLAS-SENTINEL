# ATLAS Sentinel Frontend

Vercel-ready Next.js command center for the ATLAS Sentinel MVP.

## Local Development

```bash
npm install
npm run dev
```

From the monorepo root:

```bash
npm run dev
npm run build
```

## Vercel Settings

- Framework preset: `Next.js`
- Root directory: `apps/frontend`
- Build command: `npm run build`
- Install command: `npm install`
- Output directory: leave default

The frontend is currently demo-data driven, so it can deploy without the FastAPI backend. When the backend is hosted, set `NEXT_PUBLIC_API_URL` in Vercel.
