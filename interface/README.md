# Unitron Interface

A minimal web interface to interact with the Unitron backend services.

## Development

Copy `.env.example` to `.env` and edit the value if you want to point the
interface at a different API endpoint.

```bash
# install dependencies
npm install
# copy environment template
cp .env.example .env
# start dev server
npm run dev
```

Open `http://localhost:5173` in your browser and start analyzing URLs.

## Building and running

```bash
# create optimized production build
npm run build
# ensure .env points at your API
npm start
```

The `VITE_API_BASE_URL` value in `.env` tells the frontend where the API is
running. The template points to the production deployment at
`https://unitron-production.up.railway.app`. For local development use
`http://localhost:8080`.
