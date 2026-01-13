# Deployment Guide - Bangla PDF Editor

## 🚀 Deployment Options

### Option 1: Local Development Server

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python run.py
```

Access at: `http://localhost:5000`

---

### Option 2: Production with Gunicorn

1. **Install Gunicorn**
```bash
pip install gunicorn
```

2. **Create Gunicorn config**
Create `gunicorn_config.py`:
```python
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
```

3. **Run with Gunicorn**
```bash
gunicorn -c gunicorn_config.py backend.app:app
```

---

### Option 3: Docker Deployment

1. **Create Dockerfile**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p uploads sessions exports fonts

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "run.py"]
```

2. **Build and Run**
```bash
docker build -t bangla-pdf-editor .
docker run -p 5000:5000 -v $(pwd)/uploads:/app/uploads bangla-pdf-editor
```

---

### Option 4: Nginx + Gunicorn

1. **Install Nginx**
```bash
sudo apt-get install nginx
```

2. **Create Nginx config** (`/etc/nginx/sites-available/pdf-editor`)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }
    
    location /static/ {
        alias /path/to/app/frontend/static/;
    }
}
```

3. **Enable site and restart**
```bash
sudo ln -s /etc/nginx/sites-available/pdf-editor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

### Option 5: Systemd Service

1. **Create service file** (`/etc/systemd/system/pdf-editor.service`)
```ini
[Unit]
Description=Bangla PDF Editor
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/app
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -c gunicorn_config.py backend.app:app

[Install]
WantedBy=multi-user.target
```

2. **Enable and start**
```bash
sudo systemctl enable pdf-editor
sudo systemctl start pdf-editor
sudo systemctl status pdf-editor
```

---

## 🔒 Security Considerations

### 1. SSL/HTTPS Setup
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com
```

### 2. Environment Variables
Create `.env` file:
```
SECRET_KEY=your-super-secret-key-change-this
FLASK_ENV=production
MAX_CONTENT_LENGTH=52428800
```

### 3. File Permissions
```bash
chmod 755 backend/
chmod 644 backend/*.py
chmod 700 uploads/ sessions/ exports/
```

### 4. Firewall Setup
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## 📊 Performance Optimization

### 1. Redis for Sessions
```python
# Install redis
pip install redis flask-session

# In app.py
from flask_session import Session
import redis

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')
Session(app)
```

### 2. Caching
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=300)
def expensive_operation():
    # Your code here
    pass
```

### 3. Database for Sessions
Consider using PostgreSQL or MongoDB for production session storage.

---

## 🔧 Monitoring

### 1. Logging Setup
```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('app.log', maxBytes=10000000, backupCount=3)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
```

### 2. Health Check Endpoint
```python
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'version': '1.0.0'})
```

---

## 📦 Backup Strategy

### 1. Automatic Cleanup
```python
# Add to app.py
from apscheduler.schedulers.background import BackgroundScheduler
import shutil
from datetime import datetime, timedelta

def cleanup_old_files():
    """Remove files older than 24 hours"""
    cutoff = datetime.now() - timedelta(hours=24)
    
    for folder in ['uploads', 'sessions', 'exports']:
        for file in os.listdir(folder):
            filepath = os.path.join(folder, file)
            if os.path.getmtime(filepath) < cutoff.timestamp():
                os.remove(filepath)

scheduler = BackgroundScheduler()
scheduler.add_job(cleanup_old_files, 'interval', hours=1)
scheduler.start()
```

### 2. Database Backup
```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf backup_$DATE.tar.gz uploads/ sessions/ fonts/
```

---

## 🌍 Cloud Deployment

### AWS EC2
1. Launch EC2 instance (Ubuntu 20.04)
2. SSH and install dependencies
3. Clone repository
4. Setup Nginx + Gunicorn
5. Configure security groups (ports 80, 443)

### Google Cloud Platform
1. Create Compute Engine instance
2. Follow Ubuntu deployment steps
3. Setup firewall rules

### Heroku
1. Create `Procfile`:
```
web: gunicorn backend.app:app
```

2. Deploy:
```bash
heroku create bangla-pdf-editor
git push heroku main
```

### DigitalOcean
1. Create droplet (Ubuntu)
2. One-click Docker installation
3. Deploy using Docker option

---

## 🧪 Testing Deployment

```bash
# Test health
curl http://localhost:5000/health

# Test upload
curl -X POST -F "file=@test.pdf" http://localhost:5000/api/upload

# Load testing
pip install locust
locust -f tests/load_test.py
```

---

## 📞 Troubleshooting

### Issue: Out of Memory
**Solution**: Increase worker memory or reduce DPI settings

### Issue: Slow OCR
**Solution**: Enable GPU support or cache OCR results

### Issue: File Upload Fails
**Solution**: Check Nginx `client_max_body_size` and Flask `MAX_CONTENT_LENGTH`

### Issue: Fonts Not Loading
**Solution**: Verify font file permissions and path in config

---

## 📝 Maintenance

### Regular Tasks
- Clear old sessions weekly
- Update dependencies monthly
- Review logs daily
- Backup fonts and configurations
- Monitor disk space

### Updates
```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Restart service
sudo systemctl restart pdf-editor
```

---

**For production deployment assistance, contact the development team.**
