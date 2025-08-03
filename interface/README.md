# Unitron Interface

A minimal web interface to interact with the Unitron backend services.

## Development

Copy `.env.example` to `.env` and set `VITE_API_BASE_URL` to the gateway URL.
For local development this should be `http://localhost:8080`.

```bash
# install dependencies
npm install
# copy environment template
cp .env.example .env
# ensure the frontend talks to your local gateway
echo "VITE_API_BASE_URL=http://localhost:8080" > .env
# start dev server
npm run dev
```

Open `http://localhost:5173` in your browser and start analyzing URLs.

Set `VITE_USE_JIT_DOMAINS=true` to enable the just-in-time domain scope controls.

The analyzer form includes a **Technology Stack** picker, an **Industry**
dropdown, and a **Pain Point** text box for additional context. Generated
insights can be downloaded via the **Export Markdown** button.

## Building and running

```bash
# create optimized production build
npm run build
# ensure .env points at your API
npm start
# start script uses `serve -s build` to host the static files
```

The interface **requires** `VITE_API_BASE_URL` in `.env` so it knows where the
API is running. The template now defaults to `http://localhost:8080`. Update
this value to point at your deployed gateway as needed.

The gateway's `/insight` endpoint proxies to `INSIGHT_URL`.
Make sure `OPENAI_API_KEY` is set in that service's environment so it can reach the OpenAI API.

## Insight display

The analysis result now includes an "Executive Summary" showing a short
insight fetched from the gateway. When a user clicks **Generate
Insights** the frontend calls `/insight` which returns markdown. The
markdown is rendered directly by `InsightCard`.
