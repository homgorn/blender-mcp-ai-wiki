---
id: safe_mode
lang: en
orig_lang: en
category: security
type: reference
difficulty: 0
translation: template
---
# SECURITY & SAFE MODE

> Goal: ## 🌍 MULTILANG

**ID:** safe_mode | **Lang:** en | **Orig:** en | **Category:** security | **Tags:** 

---

# SECURITY & SAFE MODE

**MCP/Blender security best practices and safe mode configuration**

---

## 🎯 THREAT MODEL

| Threat Vector | Risk | Mitigation |
|---------------|------|------------|
| **Code Injection** | Arbitrary Python execution | Safe Mode, AST validation |
| **File System Access** | Read/write/delete files | Path allowlists, sandbox |
| **Network Access** | Data exfiltration, C2 | Network policies, allowlists |
| **Process Execution** | Command injection | Subprocess blocking |
| **Data Exfiltration** | Scene data, textures | Output controls, audit logs |
| **Privilege Escalation** | Blender runs as user | User isolation, containers |
| **Supply Chain** | Malicious addons | Signed addons, verification |

---

## 🛡️ BLENDER-MCP SAFE MODE

### Server-Side Safe Mode
```bash
# Enable safe mode
BLENDER_MCP_SAFE_MODE=1 uvx blender-mcp

# Or in config
export BLENDER_MCP_SAFE_MODE=1
uvx blender-mcp
```

### What Safe Mode Blocks
```python
# Server-side validation (blender-mcp/src/safe_mode.py)

FORBIDDEN_MODULES = {
    'os', 'sys', 'subprocess', 'socket', 'urllib', 'requests',
    'importlib', 'pkgutil', 'runpy', 'zipimport',
    'threading', 'multiprocessing', 'asyncio',
    'ctypes', 'cffi', 'crypt', 'hashlib', 'secrets',
    'tempfile', 'shutil', 'glob', 'fnmatch', 'linecache',
    'pickle', 'shelve', 'dbm', 'sqlite3', 'csv',
    'configparser', 'tomllib', 'json', 'xml', 'yaml',
}

FORBIDDEN_BUILTINS = {
    'eval', 'exec', 'compile', 'open', '__import__',
    'getattr', 'setattr', 'delattr', 'globals', 'locals',
    'vars', 'dir', 'help', 'breakpoint',
}

FORBIDDEN_BPY = {
    'bpy.ops.wm.open_mainfile',
    'bpy.ops.wm.save_as_mainfile',
    'bpy.ops.wm.read_factory_settings',
    'bpy.ops.script.python_file_run',
    'bpy.ops.text.run_script',
    'bpy.app.handlers',
    'bpy.app.timers',
    'bpy.app.driver_namespace',
    'bpy.utils.register_class',
    'bpy.utils.unregister_class',
    'bpy.types',
    'bpy.data.libraries.load',
    'bpy.data.texts.new',
    'bpy.data.texts.remove',
}
```

### Safe Mode Validator
```python
# blender-mcp/src/safe_mode.py

import ast

class SafeModeValidator:
    @classmethod
    def validate_code(cls, code: str) -> tuple[bool, str]:
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        
        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    if alias.name.split('.')[0] in cls.FORBIDDEN_MODULES:
                        return False, f"Forbidden import: {alias.name}"
            
            # Check builtin calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in cls.FORBIDDEN_BUILTINS:
                        return False, f"Forbidden builtin: {node.func.id}"
                elif isinstance(node.func, ast.Attribute):
                    full_name = ast.unparse(node.func)
                    if any(full_name.startswith(f) for f in cls.FORBIDDEN_BPY):
                        return False, f"Forbidden bpy: {full_name}"
            
            # Check attribute access
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    if node.value.id == 'bpy':
                        attr_path = f"bpy.{node.attr}"
                        if any(attr_path.startswith(f) for f in cls.FORBIDDEN_BPY):
                            return False, f"Forbidden bpy access: {attr_path}"
        
        return True, "OK"
```

### Safe Mode Configuration
```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"],
      "env": {
        "BLENDER_MCP_SAFE_MODE": "1",
        "BLENDER_MCP_ALLOWED_MODULES": "bpy,bmesh,mathutils,math,random,json,uuid",
        "BLENDER_MCP_MAX_EXECUTION_TIME": "30",
        "BLENDER_MCP_MAX_MEMORY_MB": "1024"
      }
    }
  }
}
```

---

## 🔒 CLIENT-SIDE PERMISSIONS

### Permission Model
```python
class PermissionManager:
    PERMISSIONS = {
        "read_scene": [
            "get_scene_info", 
            "get_object_info", 
            "get_viewport_screenshot"
        ],
        "modify_scene": [
            "create_object", 
            "modify_object", 
            "delete_object"
        ],
        "materials": [
            "set_material", 
            "create_material"
        ],
        "assets": [
            "download_polyhaven_asset", 
            "search_polyhaven_assets"
        ],
        "ai_generation": [
            "create_rodin_job", 
            "poll_rodin_job_status"
        ],
        "code_execution": [
            "execute_blender_code"
        ],
        "admin": [
            "get_addon_info", 
            "set_telemetry_consent"
        ],
    }
    
    def __init__(self, allowed_roles: list[str]):
        self.allowed = set()
        for role in allowed_roles:
            self.allowed.update(self.PERMISSIONS.get(role, []))
    
    def check(self, tool_name: str) -> bool:
        return tool_name in self.allowed
    
    def filter_tools(self, all_tools: list) -> list:
        return [t for t in all_tools if t["name"] in self.allowed]

# Usage in OpenCode config
opencode_config = {
    "mcp": {
        "blender-mcp": {
            "type": "local",
            "command": ["uvx", "blender-mcp"],
            "enabled": True,
            "environment": {
                "BLENDER_MCP_SAFE_MODE": "1",
                "BLENDER_MCP_ROLE": "read_scene,modify_scene,materials"
            }
        }
    }
}
```

---

## 🔐 NETWORK SECURITY

### Network Policies
```python
# Network Policy for Blender-MCP
class NetworkPolicy:
    def __init__(self):
        self.allowed_domains = {
            'polyhaven.com',      # Asset downloads
            'api.poly.pizza',     # Poly Pizza API
            'api.sketchfab.com',  # Sketchfab API
            'api.hyper3d.ai',     # Hyper3D
            'api.meshy.ai',       # Meshy
        }
        self.blocked_ports = {22, 23, 3389, 4444, 5432, 3306, 6379}
        self.allowed_ports = {80, 443}
    
    def check_url(self, url: str) -> bool:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        
        # Check domain
        if parsed.netloc not in self.allowed_domains:
            return False
        
        # Check port
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        if port not in self.allowed_ports:
            return False
        
        # Block private IPs
        import ipaddress
        try:
            ip = ipaddress.ip_address(parsed.hostname)
            if ip.is_private or ip.is_loopback:
                return False
        except ValueError:
            pass  # Hostname, not IP
        
        return True

# Blocked: localhost, private IPs, non-standard ports
# Allowed: HTTPS to approved domains only
```

### API Key Management
```python
# Secure API Key Storage
import keyring
import os

class APIKeyManager:
    SERVICE = "blender-mcp"
    
    @staticmethod
    def store_key(service: str, key: str):
        keyring.set_password(APIKeyManager.SERVICE, service, key)
    
    @staticmethod
    def get_key(service: str) -> str:
        return keyring.get_password(APIKeyManager.SERVICE, service)
    
    @staticmethod
    def delete_key(service: str):
        keyring.delete_password(APIKeyManager.SERVICE, service)

# Environment variable fallback
def get_api_key(service: str) -> str:
    # Priority: keyring > env var > config file
    key = keyring.get_password("blender-mcp", service)
    if key:
        return key
    
    env_var = f"BLENDER_MCP_{service.upper()}_API_KEY"
    return os.getenv(env_var, "")
```

---

## 📋 AUDIT LOGGING

### Structured Audit Logging
```python
import structlog
import json
from datetime import datetime

class AuditLogger:
    def __init__(self, log_file="audit.log"):
        self.logger = structlog.get_logger("audit")
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
    
    def log_tool_call(self, tool_name: str, params: dict, user: str, result: dict):
        self.logger.info("tool_call", 
            timestamp=datetime.now().isoformat(),
            user=user,
            tool=tool_name,
            params=self._sanitize_params(params),
            success="error" not in result,
            error=result.get("error") if "error" in result else None
        )
    
    def log_file_access(self, user: str, path: str, operation: str):
        self.logger.info("file_access",
            timestamp=datetime.now().isoformat(),
            user=user,
            path=path,
            operation=operation
        )
    
    def log_network_request(self, user: str, url: str, method: str):
        self.logger.info("network_request",
            timestamp=datetime.now().isoformat(),
            user=user,
            url=url,
            method=method
        )
    
    def _sanitize_params(self, params: dict) -> dict:
        """Remove sensitive data from logs"""
        sanitized = {}
        sensitive_keys = {'api_key', 'password', 'token', 'secret', 'key'}
        for k, v in params.items():
            if any(s in k.lower() for s in ['key', 'password', 'token', 'secret']):
                sanitized[k] = "***REDACTED***"
            else:
                sanitized[k] = v
        return sanitized
```

### Log Analysis
```bash
# Find failed tool calls
jq 'select(.success == false) | {tool, error, timestamp}' audit.log

# Find network requests
jq 'select(.event == "network_request") | {url, method, timestamp}' audit.log

# Find file writes
jq 'select(.event == "file_access" and .operation == "write") | {path, user, timestamp}' audit.log

# Tool usage statistics
jq -r '.tool' audit.log | sort | uniq -c | sort -rn
```

---

## 🐳 CONTAINER SECURITY

### Blender in Docker (Secure)
```dockerfile
# Dockerfile.blender-secure
FROM nvidia/cuda:12.1-devel-ubuntu22.04

# Non-root user
RUN useradd -m -u 1000 -s /bin/bash blender
USER blender

# Install Blender
RUN apt-get update && apt-get install -y \
    blender \
    xvfb \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps as user
USER blender
RUN pip install --user \
    bpy-sdk \
    pynvml \
    psutil

# Working directory
WORKDIR /home/blender/work

# Entry point
ENTRYPOINT ["xvfb-run", "-a", "blender", "-b"]
CMD ["--help"]
```

### Docker Compose (Secure)
```yaml
# docker-compose.secure.yml
version: '3.8'
services:
  blender-mcp:
    build: .
    user: "1000:1000"
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
      - /home/blender/work
    cap_drop:
      - ALL
    network_mode: "none"  # No network by default
    volumes:
      - ./scenes:/home/blender/work/scenes:ro
      - ./output:/home/blender/work/output:rw
    environment:
      - BLENDER_MCP_SAFE_MODE=1
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          memory: 2G

  # Network access only for asset download
  blender-mcp-network:
    extends: blender-mcp
    network_mode: "bridge"
    environment:
      - BLENDER_MCP_ALLOWED_DOMAINS=polyhaven.com,api.poly.pizza
```

---

## 🔍 VULNERABILITY SCANNING

### Dependency Scanning
```bash
# Scan Python dependencies
pip install safety bandit
safety check -r requirements.txt
bandit -r scripts/ -f json -o bandit-report.json

# Scan Docker image
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image blender-mcp:latest

# Scan Blender addons
python -m py_compile scripts/*.py
```

### Runtime Monitoring
```python
# Runtime security monitor
import threading
import time

class SecurityMonitor:
    def __init__(self):
        self.alerts = []
        self.running = False
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._monitor, daemon=True)
        self.thread.start()
    
    def _monitor(self):
        while self.running:
            # Check for suspicious activity
            self.check_process_tree()
            self.check_file_access()
            self.check_network_connections()
            time.sleep(5)
    
    def check_process_tree(self):
        import psutil
        current = psutil.Process()
        children = current.children(recursive=True)
        for child in children:
            if child.name() not in ['blender', 'python', 'xvfb-run']:
                self.alert("Unexpected child process", {
                    'pid': child.pid,
                    'name': child.name(),
                    'cmdline': child.cmdline()
                })
    
    def alert(self, message, details):
        alert = {
            'timestamp': datetime.now().isoformat(),
            'level': 'WARNING',
            'message': message,
            'details': details
        }
        self.alerts.append(alert)
        # Send to SIEM/webhook
```

---

## 📋 SECURITY CHECKLIST

### Pre-Deployment
- [ ] Safe mode enabled (`BLENDER_MCP_SAFE_MODE=1`)
- [ ] Network policies configured
- [ ] API keys in keyring (not env vars)
- [ ] Audit logging enabled
- [ ] Container running as non-root
- [ ] Read-only filesystem where possible
- [ ] Resource limits set (CPU, RAM)
- [ ] Dependency scanning passed
- [ ] Container image scanned

### Runtime Monitoring
- [ ] Audit logs being collected
- [ ] Alerting on anomalies
- [ ] Resource usage monitored
- [ ] Network traffic logged
- [ ] File access audited

### Incident Response
- [ ] Incident response plan documented
- [ ] Rollback procedure tested
- [ ] Forensic evidence preservation
- [ ] Communication plan ready

---

## 🔗 LINKS

- **Blender-MCP Security:** https://github.com/ahujasid/blender-mcp/blob/main/src/safe_mode.py
- **OCIO Security:** https://opencolorio.org/
- **Docker Security:** https://docs.docker.com/engine/security/
- **Python Security:** https://python-security.readthedocs.io/
- **OWASP Python:** https://owasp.org/www-project-python-security/

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/security/safe_mode.md` |
| Russian | `multilang/ru/security/safe_mode.md` |