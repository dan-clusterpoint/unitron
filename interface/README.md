# Unitron Interface

A minimal web interface to interact with the Unitron backend services.

## Development

```bash
# install dependencies
npm install
# start dev server
VITE_API_BASE_URL=http://localhost:8080 npm run dev
```

Open `http://localhost:5173` in your browser and start analyzing URLs.

## Building and running

```bash
# create optimized production build
npm run build
# serve the static files
VITE_API_BASE_URL=http://localhost:8080 npm start
```

The `VITE_API_BASE_URL` variable tells the frontend where the API is running. By
default the Docker setup exposes the gateway at `http://localhost:8080`.
