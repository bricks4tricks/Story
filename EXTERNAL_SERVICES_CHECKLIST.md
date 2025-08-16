# External Services IP Allowlisting Checklist

## Static Outbound IP Addresses
Your LogicAndStories application makes outbound requests from these IPs:
```
35.160.120.126
44.233.151.27
34.211.200.85
```

## 🔴 CRITICAL SERVICES - IMMEDIATE ACTION REQUIRED

### Gmail SMTP Service
**Service**: `smtp.gmail.com:587`  
**Function**: Password reset emails, notifications  
**Risk Level**: 🔴 **CRITICAL** - Email functionality will completely fail

**Action Required:**
1. **Gmail Workspace Admin**: Add these 3 IPs to allowed senders list
2. **Gmail Personal**: Ensure "Less secure app access" or App Passwords work from these IPs
3. **Test email sending** after IP configuration changes

**Test Command:**
```bash
# Test email functionality
curl -X POST http://localhost:5000/api/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email":"test@yourdomain.com"}'
```

## 🟡 IMPORTANT SERVICES - MONITOR FOR ISSUES

### YouTube Video Embedding
**Service**: `youtube.com`, `www.youtube.com`  
**Function**: Video content in lessons  
**Risk Level**: 🟡 **MEDIUM** - Video features may break

**Monitor for:**
- Video embedding failures
- YouTube API rate limiting
- Content loading issues

**Test:** Check video playback in lessons after deployment

## 🟢 LOW RISK SERVICES

### LogicAndStories Frontend
**Service**: `logicandstories.com`, `www.logicandstories.com`  
**Function**: CORS, email links  
**Risk Level**: 🟢 **LOW** - Self-hosted service

## TESTING CHECKLIST

After deploying with static IPs, test these functions:

- [ ] **Email Sending**: Password reset emails work
- [ ] **Video Playback**: YouTube videos load in lessons  
- [ ] **CORS Requests**: Frontend API calls work
- [ ] **Admin Functions**: All admin features functional

## MONITORING SETUP

Set up alerts for:
- [ ] SMTP connection failures
- [ ] Video embedding errors
- [ ] API timeout errors
- [ ] Failed outbound connection attempts

## EMERGENCY CONTACTS

If services start failing after IP changes:
- **Email Provider Support**: [Gmail Workspace Support]
- **Hosting Provider**: [Your hosting service]
- **DNS Provider**: [Your DNS service]

## ROLLBACK PLAN

If static IPs cause service interruptions:
1. Document which services are failing
2. Contact hosting provider to temporarily disable IP restrictions
3. Work with service providers to allowlist IPs
4. Test thoroughly before re-enabling restrictions

## WHITELISTING INSTRUCTIONS

### Gmail Workspace
1. Admin Console → Security → Access Control → API controls
2. Add IP addresses to trusted networks
3. Configure SMTP relay settings if needed

### Custom SMTP Providers
1. Login to SMTP provider dashboard
2. Navigate to IP allowlisting/security settings
3. Add the 3 static IP addresses
4. Test email delivery

### YouTube/Google Services
1. Google Cloud Console → IAM & Admin → Conditional Access
2. Configure IP-based access policies if using YouTube API
3. Monitor quota and rate limiting

## SECURITY BENEFITS

✅ **Predictable Traffic**: All outbound requests from known IPs  
✅ **Enhanced Monitoring**: Easy to track and log outbound connections  
✅ **Partner Security**: External services can implement IP-based security  
✅ **Audit Trail**: Clear source attribution for all external requests