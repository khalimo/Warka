# Warka Frontend

Next.js 14 frontend for Warka's public reader experience.

## Local Development

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Required environment variables:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

## Production

Deploy to Vercel or Render Static/Web hosting with:

```text
NEXT_PUBLIC_API_BASE_URL=https://your-backend.onrender.com
NEXT_PUBLIC_SITE_URL=https://your-frontend-domain.com
```

The frontend expects the backend API contract to remain in snake_case and uses a mapper layer to transform responses for the UI.
