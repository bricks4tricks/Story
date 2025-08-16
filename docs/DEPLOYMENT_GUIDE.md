# Deployment Guide for Render

This guide covers deploying LogicAndStories to Render with PostgreSQL.

## Prerequisites

1. Render account
2. GitHub repository with your code
3. PostgreSQL database on Render

## Environment Variables

Set these environment variables in your Render service:

### Required Variables
```bash
# Database (automatically provided by Render PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/database

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Email Configuration (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com

# Frontend URL
FRONTEND_BASE_URL=https://your-app.onrender.com

# Security
CSRF_SECRET_KEY=another-secret-key-here
```

### Optional Variables
```bash
# Logging
LOG_LEVEL=INFO

# Rate Limiting (if using Redis)
REDIS_URL=redis://...
```

## Deployment Steps

### 1. Create PostgreSQL Database
1. Go to Render Dashboard
2. Click "New" → "PostgreSQL"
3. Choose a name and region
4. Note the connection details

### 2. Create Web Service
1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: `logicandstories`
   - **Region**: Same as your database
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python render_deploy.py`
   - **Start Command**: `gunicorn -c gunicorn.conf.py app:app`

### 3. Environment Setup
1. Add all environment variables listed above
2. Set `DATABASE_URL` to your PostgreSQL connection string
3. Generate secure values for `SECRET_KEY` and `CSRF_SECRET_KEY`

### 4. Build and Deploy
The deployment process will:
1. Install Python dependencies
2. Build CSS assets (if Node.js available)
3. Run database migrations
4. Start the application

## Build Script Details

The `render_deploy.py` script handles:
- Environment validation
- Dependency installation
- CSS building with Tailwind
- Database migrations
- Health checks

## Database Migrations

Migrations run automatically on deployment. To run manually:
```bash
python migration_manager.py migrate
```

## Monitoring

### Health Check
The app provides a health endpoint at `/health` that Render uses for monitoring.

### Logs
View logs in the Render dashboard under your service's "Logs" tab.

### Admin Audit Logs
Admin actions are logged to the database for security auditing.

## Performance Optimization

### Connection Pooling
- Configured for 2-20 connections in production
- Optimized for Render's infrastructure

### Caching
- Static assets are served efficiently
- Database queries are optimized with indexes

### Security Headers
- Comprehensive security headers are applied
- HTTPS is enforced
- CSRF protection is enabled

## SSL/TLS Configuration

Render provides automatic HTTPS. The application is configured to:
- Enforce HTTPS in production
- Set secure cookie flags
- Use HSTS headers

## Scaling

### Horizontal Scaling
- The app is stateless and can be scaled horizontally
- Session data is stored in the database

### Database Scaling
- Use Render's PostgreSQL scaling options
- Connection pooling handles increased load

## Backup Strategy

### Database Backups
- Render provides automatic daily backups
- Point-in-time recovery available
- Manual backups can be created

### Code Backups
- Code is versioned in Git
- Deployment history is tracked in Render

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify `DATABASE_URL` format
   - Check network connectivity
   - Ensure SSL is enabled

2. **Migration Failures**
   - Check database permissions
   - Verify migration file syntax
   - Review migration logs

3. **Build Failures**
   - Check `requirements.txt` format
   - Verify Python version compatibility
   - Review build logs

### Debug Mode
Set `FLASK_ENV=development` temporarily for detailed error messages.

### Log Analysis
Common log patterns:
- `Admin action:` - Admin audit trail
- `Session creation` - User authentication
- `Migration` - Database changes

## Security Checklist

- [ ] Environment variables are set securely
- [ ] Database uses SSL connections
- [ ] HTTPS is enforced
- [ ] Security headers are configured
- [ ] Admin sessions are properly secured
- [ ] Audit logging is enabled
- [ ] Rate limiting is configured

## Maintenance

### Regular Tasks
1. Monitor application logs
2. Review admin audit logs
3. Check database performance
4. Update dependencies as needed

### Updates
1. Test changes in development
2. Update version in Git
3. Deploy through Render dashboard
4. Monitor deployment logs
5. Verify functionality

## Support

For deployment issues:
1. Check Render documentation
2. Review application logs
3. Verify environment configuration
4. Test database connectivity