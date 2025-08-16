# Database Security Configuration

## Static Outbound IP Addresses

Your LogicAndStories application will connect to the database from these static IP addresses:

```
35.160.120.126
44.233.151.27
34.211.200.85
```

## Database Firewall Configuration

### ✅ REQUIRED: Configure IP Allowlist

Your managed database service should be configured to **ONLY** accept connections from the above IP addresses.

**PostgreSQL Connection String:**
```
postgresql://root:5ijBwqeThiTcfMLbo6cofrSExSZ8FrXg@dpg-d24k1tbe5dus73dccms0-a/educational_platform_db_0z56
```

### 🚨 Security Checklist

- [ ] Database firewall configured to block all IPs except the 3 static IPs above
- [ ] SSL/TLS encryption enforced (✅ already configured via `sslmode=require`)
- [ ] Database credentials rotated regularly
- [ ] Connection monitoring enabled
- [ ] Failed connection attempt alerts configured

### Network Security

#### Current Security Measures:
✅ **SSL Required**: `sslmode=require` enforced in `db_utils.py`  
✅ **Connection Pooling**: Configured with keepalive settings  
✅ **Environment Variables**: Database credentials not hardcoded  

#### Recommended Additional Measures:
- **IP Allowlisting**: Restrict database access to the 3 static IPs only
- **Connection Rate Limiting**: Prevent brute force attacks
- **Audit Logging**: Log all database connections and failed attempts
- **Network Monitoring**: Monitor for connections from unauthorized IPs

### Emergency Response

If unauthorized database access is detected:
1. Immediately rotate database credentials
2. Review database access logs
3. Check for data exfiltration
4. Verify IP allowlist configuration
5. Update `DATABASE_URL` environment variable with new credentials

### Contact Information

For database security issues, ensure your team has access to:
- Database management console
- IP allowlist configuration
- Credential rotation procedures
- Monitoring and alerting systems