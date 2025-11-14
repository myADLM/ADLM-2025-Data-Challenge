# Flask SOP Query - Gunicorn Production Setup 🚀

The Flask SOP Query application now supports **Gunicorn** for production deployment, allowing it to run as a background service without requiring an active terminal session.

## 🌟 New Features

- **Background Service**: Runs independently without terminal
- **Multiple Workers**: Better performance with concurrent requests
- **Auto-Restart**: Workers restart automatically to prevent memory leaks
- **Production Ready**: Proper logging and process management
- **Service Control**: Easy start/stop/restart/status commands

## 🚀 Quick Start

### Method 1: Background Service (Recommended)

```bash
cd /labs/jupyter/ai_challenge/flask

# Start the service in background
./service.sh start

# Check service status
./service.sh status

# View real-time logs
./service.sh logs

# Stop the service
./service.sh stop
```

### Method 2: Interactive Gunicorn

```bash
cd /labs/jupyter/ai_challenge/flask
./start_gunicorn.sh
```

### Method 3: Development Server (Flask built-in)

```bash
cd /labs/jupyter/ai_challenge/flask
./start.sh
# or
python app.py --debug
```

## 🌐 Access URLs

- **Local**: `http://localhost:5000`
- **Network**: `http://10.252.96.40:5000`

## 🔧 Service Management Commands

```bash
# Service control
./service.sh start      # Start background service
./service.sh stop       # Stop background service  
./service.sh restart    # Restart service
./service.sh status     # Check if running
./service.sh logs       # View real-time logs

# Check what's running
ps aux | grep gunicorn
```

## 📁 File Structure

```
flask/
├── app.py                 # Main Flask application
├── gunicorn.conf.py       # Gunicorn configuration
├── service.sh             # Background service control
├── start_gunicorn.sh      # Interactive Gunicorn startup
├── start.sh              # Development server startup
├── requirements.txt       # Dependencies (includes Gunicorn)
└── templates/            # Web interface templates
```

## ⚙️ Configuration

### Gunicorn Settings (`gunicorn.conf.py`)

- **Workers**: `(CPU cores × 2) + 1` for optimal performance
- **Bind**: `0.0.0.0:5000` for external access
- **Timeout**: 30 seconds for LLM processing
- **Auto-restart**: Workers restart after 1000 requests
- **Logging**: Output to stdout/stderr with detailed access logs

### Service Settings

- **PID File**: `/tmp/gunicorn_flask_sop.pid`
- **Log File**: `/tmp/gunicorn_flask_sop.log`  
- **Process Name**: `flask_sop_query`

## 🔍 Monitoring

### Check Service Status
```bash
./service.sh status
```

### View Logs
```bash
# Real-time logs
./service.sh logs

# Log file directly
tail -f /tmp/gunicorn_flask_sop.log

# Check for errors
grep ERROR /tmp/gunicorn_flask_sop.log
```

### Process Information
```bash
# Find Gunicorn processes
ps aux | grep gunicorn

# Check port usage
netstat -tlnp | grep :5000
```

## 🚧 Troubleshooting

### Service Won't Start
```bash
# Check if virtual environment exists
ls -la ../yjacobs/.venv/

# Check dependencies
source ../yjacobs/.venv/bin/activate
pip list | grep gunicorn

# Check logs for errors
tail -20 /tmp/gunicorn_flask_sop.log
```

### Service Running But Can't Access
```bash
# Check if service is listening
netstat -tlnp | grep :5000

# Check firewall (if applicable)
sudo ufw status

# Try local access first
curl http://localhost:5000
```

### Performance Issues
```bash
# Check worker count
ps aux | grep "gunicorn.*worker" | wc -l

# Monitor resource usage
top -p $(cat /tmp/gunicorn_flask_sop.pid)

# Restart workers
./service.sh restart
```

## 🔒 Security Considerations

- **HTTP Only**: Gunicorn serves HTTP (add reverse proxy for HTTPS)
- **Internal Network**: Accessible on local network (10.252.96.40)
- **No Authentication**: Designed for internal lab use
- **Process Isolation**: Each worker runs in separate process

## 🔄 Auto-Start on Boot (Optional)

To make the service start automatically on system boot:

```bash
# Add to crontab
crontab -e

# Add this line:
@reboot /labs/jupyter/ai_challenge/flask/service.sh start
```

## 📊 Performance Comparison

| Method | Workers | Memory | CPU | Background | Production |
|--------|---------|--------|-----|------------|------------|
| Flask Dev | 1 | Low | Low | ❌ | ❌ |
| Gunicorn Interactive | Multi | Medium | Medium | ❌ | ✅ |
| Gunicorn Service | Multi | Medium | Medium | ✅ | ✅ |

## 💡 Usage Examples

```bash
# Start service and check immediately
./service.sh start && ./service.sh status

# Start service and monitor logs
./service.sh start && ./service.sh logs

# Quick restart with status check
./service.sh restart && sleep 2 && ./service.sh status

# Stop service and verify
./service.sh stop && ps aux | grep gunicorn
```

## 🎯 Next Steps

1. **Start the service**: `./service.sh start`
2. **Check status**: `./service.sh status`
3. **Access the web interface**: `http://10.252.96.40:5000`
4. **Select SOP files and start querying!**

The Flask SOP Query application is now production-ready with Gunicorn! 🎉
