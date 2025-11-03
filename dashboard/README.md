# FastAPI Monitoring Dashboard

Simple Streamlit dashboard for monitoring ECS-hosted FastAPI applications.

## Setup

```bash
pip install -r requirements.txt
```

## Configure Secrets

Copy the example secrets file and add your values:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` with your AWS resource names:
- AWS Region
- AWS Access Key ID and Secret Access Key
- ECS Cluster Name
- ECS Service Name
- ALB Name (format: `app/your-alb/xxx`)
- CloudFront Distribution ID
- CloudWatch Log Group Name

## Run Locally

**Option 1: Dashboard only**
```bash
streamlit run app.py
```

**Option 2: With FastAPI app**
```bash
# Terminal 1 - FastAPI
cd app
uvicorn main:app --port 8000

# Terminal 2 - Dashboard
cd dashboard
streamlit run app.py --server.port 8501
```

**Option 3: Both together**
```bash
python run_both.py
```

Access:
- API: http://localhost:8000
- Dashboard: http://localhost:8501

## Deploy to Streamlit Cloud

1. Push to GitHub (secrets are gitignored)
2. Connect repo at [share.streamlit.io](https://share.streamlit.io)
3. Add secrets in app settings (copy from your local `secrets.toml`)

## Metrics Displayed

- ECS: CPU, Memory, Running Tasks
- ALB: Request count, Latency, 5XX errors
- CloudFront: Requests, Cache hit rate, Error rate
- Logs: API endpoint performance and status codes
