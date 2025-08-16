# LogicAndStories Deployment Guide

This guide covers deployment options for the LogicAndStories application.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git (for cloning the repository)
- Node.js (for CSS compilation)

### 1. Environment Setup
1. Copy `.env.example` to `.env`
2. Fill in your production values:
   ```bash
   # Database
   DATABASE_URL=postgresql://user:password@host:port/database
   
   # SMTP Settings
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   SENDER_EMAIL=your-email@gmail.com
   
   # App Settings
   FRONTEND_BASE_URL=https://yourdomain.com
   ADMIN_PASSWORD=secure-admin-password
   ```

### 2. One-Command Deployment
```bash
./deploy.sh
```

This script will:
- ✅ Validate environment configuration
- 🔒 Run security tests
- 📦 Build CSS assets
- 🐳 Build Docker image
- 🚀 Deploy the application
- 🏥 Perform health checks

## 📋 Deployment Options

### Option 1: Docker Compose (Recommended)
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 2: Manual Docker Deployment
```bash
# Build image
docker build -t logicandstories .

# Run container
docker run -d \
  --name logicandstories \
  -p 5000:5000 \
  --env-file .env \
  logicandstories
```

### Option 3: GitHub Actions (CI/CD)
Push to `main` branch triggers automatic deployment via `.github/workflows/deploy.yml`.

Required secrets:
- `DATABASE_URL`
- `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`
- `PRODUCTION_HOST`, `PRODUCTION_USER`, `PRODUCTION_SSH_KEY`
- `REGISTRY_URL`, `REGISTRY_USERNAME`, `REGISTRY_PASSWORD`

### Option 4: Local Development
```bash
# Install dependencies
pip install -r requirements.txt
npm install

# Build CSS
npm run build:css

# Set environment variables
export FLASK_ENV=development
export FLASK_APP=app.py

# Run application
python app.py
```

## 🔧 Production Considerations

### Security Checklist
- [ ] All environment variables set securely
- [ ] Database uses SSL connections
- [ ] Admin endpoints require authentication
- [ ] SMTP credentials are app-specific passwords
- [ ] Container runs as non-root user
- [ ] Firewall configured properly

### Performance Optimizations
- [ ] Use a reverse proxy (nginx/Apache)
- [ ] Enable gzip compression
- [ ] Set up CDN for static assets
- [ ] Configure database connection pooling
- [ ] Monitor application metrics

### Monitoring & Logging
- [ ] Set up application monitoring (Prometheus/Grafana)
- [ ] Configure centralized logging
- [ ] Set up error alerting
- [ ] Monitor database performance
- [ ] Track security events

## 🛠️ Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check database connectivity
docker-compose exec web python -c "from app import app; print('DB OK')"

# Check database logs
docker-compose logs db
```

#### Email Not Sending
```bash
# Test SMTP configuration
python test_email_setup.py
```

#### Permission Errors
```bash
# Check container logs
docker-compose logs web

# Check file permissions
ls -la
```

### Health Checks
- Application: `http://your-domain/health`
- Database: `docker-compose exec db pg_isready`

## 📊 Monitoring

### Application Metrics
- Response times
- Error rates
- Database connections
- Memory usage
- Security events

### Security Monitoring
- Failed authentication attempts
- Admin access logs
- Database access patterns
- Unusual API usage

## 🔄 Updates & Maintenance

### Rolling Updates
```bash
# Pull latest code
git pull origin main

# Run deployment
./deploy.sh
```

### Database Migrations
```bash
# Create backup
docker-compose exec db pg_dump -U postgres database_name > backup.sql

# Run migrations
python migrate.py
```

### Security Updates
```bash
# Update dependencies
pip-audit
npm audit

# Run security tests
python test_admin_security.py
python test_admin_py_security.py
```

## 📞 Support

For deployment issues:
1. Check application logs: `docker-compose logs -f web`
2. Verify environment variables: `python env_validator.py`
3. Run security tests: `./test_security.sh`
4. Check database connectivity
5. Review this deployment guide

## 🔐 Security Notes

- Never commit `.env` files to git
- Use strong passwords for admin accounts
- Regularly update dependencies
- Monitor for security vulnerabilities
- Keep database credentials secure
- Use HTTPS in production
- Regular security audits recommended