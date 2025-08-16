# Google Workspace Email Setup for LogicAndStories

## Email Configuration
**Admin Email**: `admin@bricks4tricks.com` (for authentication)  
**Sender Email**: `noreply@logicandstories.com` (alias for outgoing emails)
**Domain**: `bricks4tricks.com`  
**Service**: Google Workspace  

## Static IP Addresses That Need Allowlisting
```
35.160.120.126
44.233.151.27
34.211.200.85
```

## 🔧 SETUP STEPS

### Step 1: Create App Password
1. Go to [Google Admin Console](https://admin.google.com)
2. Navigate to **Security** → **2-Step Verification** 
3. Click **App passwords**
4. Generate new app password for "LogicAndStories SMTP"
5. Copy the 16-character password (save securely)

### Step 2: Configure IP Allowlisting (CRITICAL)
1. **Admin Console** → **Security** → **Access and data control** → **API controls**
2. Click **Manage Domain-wide Delegation**
3. Navigate to **IP allowlisting** section
4. Add these IP addresses:
   ```
   35.160.120.126/32
   44.233.151.27/32
   34.211.200.85/32
   ```

### Step 3: SMTP Relay Configuration (Recommended)
1. **Admin Console** → **Apps** → **Google Workspace** → **Gmail** → **Routing**
2. Click **Add Route** for SMTP relay
3. **Allowed senders**: Add the 3 static IP addresses
4. **Authentication**: Require SMTP AUTH
5. **Encryption**: Require TLS encryption

### Step 4: Environment Variables
Update your production `.env` file:
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=admin@bricks4tricks.com
SMTP_PASSWORD=your_16_character_app_password
SENDER_EMAIL=noreply@logicandstories.com
FRONTEND_BASE_URL=https://logicandstories.com
```

## 🧪 TESTING

### Test 1: SMTP Connection
```bash
# Test SMTP connectivity
python -c "
import smtplib
import os
from email.mime.text import MIMEText

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('admin@bricks4tricks.com', 'your_app_password')
    print('✅ SMTP connection successful!')
    server.quit()
except Exception as e:
    print(f'❌ SMTP connection failed: {e}')
"
```

### Test 2: Password Reset Email
```bash
# Test password reset functionality
curl -X POST https://logicandstories.com/api/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bricks4tricks.com"}'
```

### Test 3: Email Delivery
1. Trigger a password reset
2. Check `admin@bricks4tricks.com` inbox
3. Verify email contains proper reset link
4. Test that reset link works

## 🚨 TROUBLESHOOTING

### Common Issues:

**❌ "Authentication failed"**
- Verify app password is correct (16 characters, no spaces)
- Ensure 2FA is enabled on Google Workspace account
- Check that SMTP is enabled for the domain

**❌ "Connection refused"**
- Verify static IPs are allowlisted in Google Workspace
- Check that port 587 is not blocked by firewall
- Confirm SMTP relay is configured for the IPs

**❌ "Sender domain not allowed"**
- Ensure `admin@bricks4tricks.com` is verified in Google Workspace
- Check domain ownership in Google Admin Console
- Verify sender email matches SMTP username

### Emergency Fallback:
If Google Workspace blocks the static IPs:
1. **Temporary**: Use a different SMTP provider (SendGrid, Mailgun)
2. **Contact Google Support** with static IP addresses
3. **Verify domain ownership** in Google Admin Console

## 🔒 SECURITY BENEFITS

✅ **Domain Authentication**: Emails from verified `@bricks4tricks.com` domain  
✅ **Professional Appearance**: No "via gmail.com" warnings  
✅ **Enhanced Deliverability**: Better inbox placement  
✅ **IP Allowlisting**: Only authorized servers can send emails  
✅ **Audit Trail**: Google Workspace logs all email activity  

## 📧 EMAIL TEMPLATES

### Password Reset Email
**From**: admin@bricks4tricks.com  
**Subject**: Logic and Stories - Password Reset  
**Content**: Professional branded email with reset link

### System Notifications
**From**: admin@bricks4tricks.com  
**Purpose**: User registration, system alerts, admin notifications

## PRODUCTION CHECKLIST

Before going live with static IPs:
- [ ] App password generated and saved securely
- [ ] Static IPs allowlisted in Google Workspace
- [ ] SMTP relay configured (optional but recommended)
- [ ] Production environment variables updated
- [ ] Email sending tested from production environment
- [ ] Password reset flow tested end-to-end
- [ ] Email deliverability verified (check spam folders)
- [ ] Google Workspace security settings reviewed