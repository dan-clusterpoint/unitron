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

The gateway's `/insight` endpoint calls `/generate-insights` on the insight service.
Make sure `OPENAI_API_KEY` is set in that service's environment so it can reach the OpenAI API.

## Insight display

The analysis result now includes an "Executive Summary" showing a short
insight fetched from the gateway. When a user clicks **Generate
Insights** the frontend calls `/generate-insight-and-personas`. The
response may vary, so `parseInsightPayload` in `src/utils` normalizes
the data. The parsed result is then passed to `InsightCard` which renders
the summary, recommended actions and any personas.
