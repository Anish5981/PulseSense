# Start the Data Layer (Docker containers)
Write-Host "Starting Data Layer (Kafka, TimescaleDB, Grafana)..." -ForegroundColor Cyan
docker-compose up -d zookeeper kafka timescaledb grafana

# Wait a few seconds for Kafka and DB to boot up
Start-Sleep -Seconds 10

# Start the Sentiment Engine in a new window
Write-Host "Starting AI Sentiment Engine..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python execution\processing\sentiment_engine.py"

# Start the HackerNews Streamer in a new window
Write-Host "Starting HackerNews Streamer..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python execution\ingestion\hackernews_streamer.py"

# Start the Database Sink in a new window
Write-Host "Starting Database Writer..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python execution\processing\standalone_sink.py"

Write-Host "Pipeline is running! You can view the dashboard at http://localhost:3000" -ForegroundColor Green
