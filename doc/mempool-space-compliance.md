# mempool.space Compliance and Best Practices

## Overview

This document outlines the compliance requirements and best practices for using mempool.space API services to ensure your account remains in good standing with the network.

## Rate Limits and API Compliance

### Official Rate Limits

**mempool.space Public API:**
- **250 requests per minute per IP address**
- Exceeding this limit will result in HTTP 429 (Too Many Requests) errors
- Repeated violations may result in temporary or permanent IP bans

### Implementation Requirements

To comply with mempool.space rate limits, implement the following in your applications:

1. **Rate Limiting on Client Side**
   ```python
   import time
   from collections import deque
   
   class RateLimiter:
       def __init__(self, max_requests=250, time_window=60):
           self.max_requests = max_requests
           self.time_window = time_window
           self.requests = deque()
       
       def allow_request(self):
           now = time.time()
           # Remove requests older than time window
           while self.requests and self.requests[0] < now - self.time_window:
               self.requests.popleft()
           
           if len(self.requests) < self.max_requests:
               self.requests.append(now)
               return True
           return False
   ```

2. **Error Handling**
   ```python
   def make_api_request(url):
       response = requests.get(url)
       
       if response.status_code == 429:
           # Rate limit exceeded
           retry_after = response.headers.get('Retry-After', 60)
           print(f"Rate limit exceeded. Retry after {retry_after} seconds")
           time.sleep(int(retry_after))
           return make_api_request(url)  # Retry
       
       return response
   ```

3. **Request Batching and Caching**
   - Cache responses to avoid redundant API calls
   - Batch related requests when possible
   - Use WebSocket connections for real-time updates instead of polling

### Best Practices

#### 1. Use Self-Hosted Instance for High Volume

If you need more than 250 requests/minute:
- Deploy your own mempool.space instance (see `contrib/mempool-space/README.md`)
- Connect to your own Bitcoin Core node
- No rate limits on self-hosted instances

#### 2. Implement Exponential Backoff

```python
def exponential_backoff(func, max_retries=5):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            wait_time = 2 ** attempt  # 1, 2, 4, 8, 16 seconds
            time.sleep(wait_time)
    raise Exception("Max retries exceeded")
```

#### 3. Use WebSocket for Real-Time Data

Instead of polling:
```javascript
// Don't do this (high rate limit usage)
setInterval(() => {
    fetch('/api/mempool/recent')
}, 1000);  // 60 requests per minute!

// Do this instead (WebSocket)
const ws = new WebSocket('wss://mempool.space/api/v1/ws');
ws.onmessage = (event) => {
    // Handle real-time updates
};
```

## Terms of Service Compliance

### Acceptable Use

✅ **Allowed:**
- Personal use and research
- Building applications that respect rate limits
- Self-hosting for commercial use
- Contributing to the open-source project

❌ **Not Allowed:**
- Excessive API abuse beyond rate limits
- Scraping without proper rate limiting
- Reselling API access
- DDoS or malicious requests

### Attribution

When using mempool.space API or data:
- Provide attribution to mempool.space
- Link back to https://mempool.space when displaying their data
- Respect their branding guidelines

Example attribution:
```html
<p>Data provided by <a href="https://mempool.space">mempool.space</a></p>
```

## Enterprise Plans

For commercial or high-volume usage:
- Contact mempool.space directly for enterprise plans
- Custom rate limits available
- Dedicated support
- SLA guarantees

Contact: Check https://mempool.space for current contact information

## Self-Hosting Compliance

When self-hosting mempool.space:

1. **Follow License Requirements**
   - mempool.space is open source (GNU AGPLv3)
   - Review license terms at https://github.com/mempool/mempool

2. **Resource Requirements**
   - Adequate server resources for Bitcoin Core + mempool.space
   - See `doc/repository-integration-guide.md` for setup

3. **Network Considerations**
   - Run your own Bitcoin Core node
   - Don't overload public infrastructure

## Monitoring and Alerts

### Track Your API Usage

```python
import logging

class APIUsageMonitor:
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        
    def log_request(self, status_code):
        self.request_count += 1
        
        if status_code == 429:
            self.error_count += 1
            logging.warning(f"Rate limit hit. Total: {self.error_count}")
        
        # Alert if hitting limits frequently
        if self.error_count > 10:
            logging.critical("Excessive rate limit errors! Review implementation.")
```

### Set Up Alerts

Configure alerts for:
- HTTP 429 responses
- Approaching rate limit threshold (e.g., 200 requests/minute)
- API errors or timeouts
- Self-hosted instance issues

## Security Best Practices

### API Key Management (if applicable)

1. **Never commit credentials to repositories**
   - Use environment variables
   - Use secrets management systems
   - See `CREDENTIALS-MANAGEMENT-TEMPLATE.md`

2. **Rotate credentials regularly**
   - Change API keys periodically
   - Update all dependent systems

3. **Monitor for unauthorized access**
   - Check API logs regularly
   - Set up alerts for unusual patterns

## Resources

### Official Documentation
- mempool.space API Docs: https://mempool.space/docs/api
- GitHub Repository: https://github.com/mempool/mempool
- Rate Limits: https://docs.mempoolnode.com/mempool-tools-suite/rate-limits

### Community
- GitHub Discussions: https://github.com/mempool/mempool/discussions
- Twitter: @mempool
- IRC/Discord: Check official website for current links

### Related Documentation
- `contrib/mempool-space/README.md` - Self-hosting guide
- `doc/mempool-space-integration.md` - Integration details
- `CREDENTIALS-MANAGEMENT-TEMPLATE.md` - Secure credential storage

## Compliance Checklist

Before deploying to production:

- [ ] Rate limiting implemented (250 req/min limit)
- [ ] Error handling for HTTP 429 responses
- [ ] Request caching implemented
- [ ] WebSocket used for real-time data (not polling)
- [ ] Exponential backoff for retries
- [ ] Usage monitoring and alerts configured
- [ ] Attribution provided where using their data
- [ ] Terms of service reviewed and understood
- [ ] Consider self-hosting for high volume needs
- [ ] No credentials stored in repository

## Troubleshooting

### "Rate limit exceeded" errors

**Problem:** HTTP 429 responses

**Solutions:**
1. Reduce request frequency
2. Implement caching
3. Use WebSocket instead of REST API polling
4. Consider self-hosting
5. Contact mempool.space for enterprise plan

### Banned IP Address

**Problem:** All requests blocked

**Solutions:**
1. Contact mempool.space support
2. Switch to self-hosted instance
3. Review and fix rate limit violations
4. Implement proper rate limiting before resuming

### Inconsistent Data

**Problem:** Data doesn't match expectations

**Solutions:**
1. Check API endpoint documentation
2. Verify Bitcoin Core is fully synced (if self-hosted)
3. Check mempool.space status page
4. Use test script: `python3 contrib/mempool-space/test-integration.py`

## Conclusion

Following these compliance guidelines ensures:
- Your account remains in good standing
- Reliable API access
- Respectful use of shared infrastructure
- Option to scale with self-hosting or enterprise plans

For questions or custom requirements, contact mempool.space directly through their official channels.
