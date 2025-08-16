# Email Domain Authentication Setup

## DMARC Issue Resolution

**Problem**: Emails from `noreply@logicandstories.com` are being blocked due to DMARC policy.

**Error**: `550 5.7.26 Unauthenticated email from logicandstories.com is not accepted due to domain's DMARC policy`

## IMMEDIATE SOLUTION (Use This Now)

Update your `.env` file to use the authenticated domain:
```bash
SENDER_EMAIL=admin@bricks4tricks.com
```

This works because `bricks4tricks.com` is properly configured in Google Workspace.

## LONG-TERM SOLUTION (For Professional Branding)

To use `noreply@logicandstories.com`, you need to configure DNS records for `logicandstories.com`:

### DNS Records Required

#### 1. SPF Record (TXT)
**Host**: `@` (root domain)  
**Value**: `v=spf1 include:_spf.google.com ~all`

#### 2. DKIM Record (TXT)
1. **Google Admin Console** → **Apps** → **Gmail** → **Authenticate email**
2. **Select domain**: `logicandstories.com`
3. **Generate DKIM key**
4. **Add the TXT record** provided by Google to your DNS

#### 3. DMARC Record (TXT)
**Host**: `_dmarc`  
**Value**: `v=DMARC1; p=none; rua=mailto:admin@bricks4tricks.com`

### Steps to Configure

#### Step 1: Add logicandstories.com to Google Workspace
1. **Google Admin Console** → **Domains** → **Add a domain**
2. **Add**: `logicandstories.com`
3. **Verify ownership** through DNS or file upload

#### Step 2: Configure Email Authentication
1. **Apps** → **Gmail** → **Authenticate email**
2. **Select**: `logicandstories.com`
3. **Generate DKIM** and add DNS record
4. **Enable** authentication

#### Step 3: Add DNS Records
Add all three records (SPF, DKIM, DMARC) to your DNS provider.

#### Step 4: Test Configuration
Use this command after DNS propagation (24-48 hours):
```bash
python test_email_setup.py
```

## CURRENT WORKING CONFIGURATION

For immediate use without DMARC issues:

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=admin@bricks4tricks.com
SMTP_PASSWORD=iojj ktaw hghg evvp
SENDER_EMAIL=admin@bricks4tricks.com
FRONTEND_BASE_URL=https://www.logicandstories.com
```

## TESTING

### Test Current Setup (Should Work)
```bash
# This should work without DMARC issues
curl -X POST https://www.logicandstories.com/api/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
```

### After DNS Configuration (Future)
```bash
# This will work after DNS setup
SENDER_EMAIL=noreply@logicandstories.com
```

## RECOMMENDATION

**For Production Launch**: 
1. Use `admin@bricks4tricks.com` initially (works immediately)
2. Set up `logicandstories.com` DNS records for future branding
3. Switch to `noreply@logicandstories.com` after DNS propagation

**Benefits of Each Approach**:
- `admin@bricks4tricks.com`: ✅ Works now, ✅ No DNS setup
- `noreply@logicandstories.com`: ✅ Professional branding, ⚠️ Requires DNS setup

## DNS PROVIDERS GUIDE

### Common DNS Providers
- **Cloudflare**: DNS Records → Add Record → TXT
- **GoDaddy**: DNS Management → TXT Records
- **Namecheap**: Advanced DNS → TXT Record
- **AWS Route 53**: Hosted Zones → Create Record → TXT

### Verification
After adding DNS records, verify with:
```bash
dig TXT logicandstories.com
dig TXT _dmarc.logicandstories.com
```