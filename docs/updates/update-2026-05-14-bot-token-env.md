# Update: Pass Bot Token via Environment Variable
**Date:** 2026-05-14
**Version:** 1.2.1.0
**Branch:** develop

## Summary
Added support for passing the Telegram bot token via `PROXMOX_BOT_TOKEN` environment variable to Docker. This simplifies deployment in containerized environments and CI/CD pipelines.

## Features

### Environment Variable Support
- `PROXMOX_BOT_TOKEN` - Pass bot token directly to Docker
- Auto-populates config on container startup
- Skips password/token setup if token provided
- Works with docker-compose and docker run

## Usage

### Docker Compose (Recommended)

**Option 1: Inline in docker-compose.yml**
```yaml
services:
  proxmox-monitor:
    environment:
      - PROXMOX_BOT_TOKEN=123456789:ABCDefghijklmnop
```

**Option 2: From .env file**
```bash
# Create .env file
echo "PROXMOX_BOT_TOKEN=123456789:ABCDefghijklmnop" > .env

# Run with env file
docker-compose up
```

**Option 3: Command line override**
```bash
PROXMOX_BOT_TOKEN="123456789:ABCDefghijklmnop" docker-compose up
```

### Docker Run

```bash
docker run -e PROXMOX_BOT_TOKEN="123456789:ABCDefghijklmnop" \
  -v $(pwd)/config:/app/config \
  proxmox-monitor:latest
```

### Kubernetes

```yaml
env:
  - name: PROXMOX_BOT_TOKEN
    valueFrom:
      secretKeyRef:
        name: proxmox-secrets
        key: bot-token
```

## How It Works

1. **Entrypoint Script** reads `PROXMOX_BOT_TOKEN` from environment
2. **Loads** config from `config.yaml` or `config/config.yaml`
3. **Updates** `telegram.token` field with environment value
4. **Saves** config back to YAML
5. **Starts** Proxmox Monitor with token configured

## Security Considerations

### ✅ Best Practices
- Use Docker secrets for sensitive data (Kubernetes/Swarm)
- Use .env files with proper permissions (600)
- Never commit tokens to git
- Use environment-specific configurations
- Consider separate tokens per environment

### ⚠️ Avoid
- Don't hardcode tokens in docker-compose.yml committed to git
- Don't pass tokens in docker run history
- Don't expose tokens in logs
- Don't share .env files

## Configuration Priority

```
1. PROXMOX_BOT_TOKEN environment variable (highest priority)
2. config.yaml file
3. Empty config (requires /setup command)
```

## Files Modified

- `Dockerfile` - Added entrypoint script
- `docker-compose.yml` - Added PROXMOX_BOT_TOKEN documentation
- `src/first_start_setup.py` - Check for env var in is_first_start()

## Testing

### Test 1: With Token
```bash
docker-compose up  # With PROXMOX_BOT_TOKEN set in .env
# Should start without setup prompt
```

### Test 2: Without Token
```bash
# Unset PROXMOX_BOT_TOKEN
docker-compose up
# Should show setup prompt
```

### Test 3: Multiple Runs
```bash
# Token persists in config after first run
docker-compose down && docker-compose up
# Token should remain
```

## Example .env File

```bash
# .env file for docker-compose
PROXMOX_BOT_TOKEN=123456789:ABCDefghijklmnopqrstuvwxyz
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
```

## CI/CD Integration

### GitHub Actions
```yaml
- name: Start container with token
  env:
    PROXMOX_BOT_TOKEN: ${{ secrets.BOT_TOKEN }}
  run: docker-compose up -d

- name: Test bot
  run: docker-compose exec proxmox-monitor /bin/bash -c "..."
```

### GitLab CI
```yaml
docker_compose_up:
  script:
    - docker-compose up -d
  variables:
    PROXMOX_BOT_TOKEN: $TELEGRAM_BOT_TOKEN
```

## Environment Variables Reference

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `PROXMOX_BOT_TOKEN` | Telegram bot token | No | `123456789:ABC...` |
| `LOG_LEVEL` | Logging level | No | `INFO`, `DEBUG`, `ERROR` |
| `PYTHONUNBUFFERED` | Unbuffered Python output | No | `1` |

## Workflow Examples

### Development Setup
```bash
# 1. Get bot token from @BotFather
BOT_TOKEN="your_token_here"

# 2. Create .env
echo "PROXMOX_BOT_TOKEN=$BOT_TOKEN" > .env

# 3. Start with compose
docker-compose up --build

# 4. No setup needed, just add allowed users with /setup
```

### Production Deployment
```bash
# 1. Store token in secrets manager
aws secrets manager create-secret --name proxmox-bot-token

# 2. Deploy with secret
docker run \
  -e PROXMOX_BOT_TOKEN="$(aws secrets get-secret-value...)" \
  proxmox-monitor:latest
```

## Troubleshooting

### Token Not Applied
```bash
# Check if env var is set
docker-compose exec proxmox-monitor env | grep PROXMOX

# Check config file
docker-compose exec proxmox-monitor cat config/config.yaml | grep token
```

### Setup Prompt Still Shows
```bash
# Check entrypoint executed
docker-compose logs | grep "Bot token found"

# Verify .env file
cat .env
```

### Permission Denied on .env
```bash
# Fix permissions
chmod 600 .env
```

## Backwards Compatibility

✅ Fully compatible with existing setups
- Works with manual config.yaml edits
- /setup command still available
- Can mix token sources (env + manual)

## Performance Impact

- Minimal - only on container startup
- YAML parsing: <100ms
- No runtime overhead

## Future Enhancements

- Support for other config fields via env vars
- Secure token validation
- Token rotation support
- Multi-token support for multiple instances

## Related Documentation

- [DOCKER_SETUP.md](../DOCKER_SETUP.md) - Docker usage
- [QUICK_START.md](../QUICK_START.md) - Getting started
- Docker secrets management

## Files Changed

- `Dockerfile` (34 → 50 lines) - Added entrypoint script
- `docker-compose.yml` (36 → 40 lines) - Added token documentation
- `src/first_start_setup.py` (258 → 275 lines) - Check env var

---

**Status:** ✅ Implemented and ready
**Ready for:** Production use with CI/CD
**Impact:** Low risk - optional feature
