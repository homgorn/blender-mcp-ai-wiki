---
lang: en
---
# MCP ADVANCED: STREAMING & TOOL COMPOSITION

**Advanced MCP patterns for production AI agents working with Blender**

---

## 🎯 STREAMING RESPONSES

### Real-time Tool Output
```python
# MCP Client with streaming support
class StreamingMCPClient:
    def __init__(self, server_cmd: list[str]):
        self.process = await asyncio.create_subprocess_exec(
            *server_cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    
    async def stream_tool(self, tool_name: str, params: dict):
        """Yield partial results as they arrive"""
        request = {
            "jsonrpc": "2.0",
            "id": uuid.uuid4().hex,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": params}
        }
        
        self.process.stdin.write((json.dumps(request) + "\n").encode())
        await self.process.stdin.drain()
        
        buffer = ""
        async for line in self.process.stdout:
            line = line.decode().strip()
            if not line:
                continue
            try:
                response = json.loads(line)
                if "result" in response:
                    # Stream partial content
                    if isinstance(response["result"], str):
                        for chunk in response["result"].split():
                            yield chunk + " "
                    else:
                        yield json.dumps(response["result"])
                break
            except json.JSONDecodeError:
                continue  # Incomplete JSON, wait for more
```

### Progressive Scene Building
```python
# Build complex scene incrementally with feedback
async def build_scene_progressively(client, scene_description: str):
    steps = [
        ("Analyzing requirements", analyze_requirements),
        ("Creating base geometry", create_base_geometry),
        ("Adding materials", apply_materials),
        ("Setting up lighting", setup_lighting),
        ("Configuring camera", setup_camera),
        ("Final render", render_scene),
    ]
    
    for step_name, step_func in steps:
        yield {"status": "progress", "step": step_name}
        result = await step_func()
        yield {"status": "step_complete", "step": step_name, "result": result}
    
    yield {"status": "complete", "scene": "ready"}
```

---

## 🔗 TOOL COMPOSITION (PIPELINES)

### Sequential Pipeline
```python
class MCPipeline:
    def __init__(self, client):
        self.client = client
        self.steps = []
    
    def add_step(self, tool_name: str, params_map: Callable):
        """params_map: (prev_result) -> next_params"""
        self.steps.append((tool_name, params_map))
        return self
    
    async def run(self, initial_params: dict):
        result = initial_params
        for tool_name, params_map in self.steps:
            params = params_map(result)
            result = await self.client.call_tool(tool_name, params)
            if "error" in result:
                raise PipelineError(f"{tool_name} failed: {result['error']}")
        return result

# Usage: Search → Download → Import → Material
pipeline = MCPipeline(client) \
    .add_step("search_polyhaven_assets", lambda r: {
        "asset_type": "models", "categories": ["chair"], "query": r["query"]
    }) \
    .add_step("download_polyhaven_asset", lambda r: {
        "asset_id": r["results"][0]["id"], 
        "asset_type": "models", 
        "resolution": "2k"
    }) \
    .add_step("set_material", lambda r: {
        "object_name": r["imported_object"],
        "material_name": "Mat_Chair",
        "color": [0.8, 0.6, 0.4, 1.0]
    })

result = await pipeline.run({"query": "modern office chair"})
```

### Parallel Execution with Dependency Graph
```python
class DependencyGraph:
    def __init__(self):
        self.nodes = {}  # tool_name -> {params, deps: []}
    
    def add(self, name: str, params: dict, depends_on: list[str] = None):
        self.nodes[name] = {"params": params, "deps": depends_on or []}
    
    async def execute(self, client):
        completed = {}
        pending = set(self.nodes.keys())
        
        while pending:
            # Find ready nodes (all deps completed)
            ready = [
                name for name in pending
                if all(dep in completed for dep in self.nodes[name]["deps"])
            ]
            
            if not ready:
                raise CircularDependencyError()
            
            # Execute ready nodes in parallel
            tasks = [
                client.call_tool(name, self.nodes[name]["params"])
                for name in ready
            ]
            results = await asyncio.gather(*tasks)
            
            for name, result in zip(ready, results):
                completed[name] = result
                pending.remove(name)
        
        return completed

# Usage: Parallel asset downloads
graph = DependencyGraph()
graph.add("download_chair", {"asset_id": "chair_01", "type": "models"}, [])
graph.add("download_table", {"asset_id": "table_01", "type": "models"}, [])
graph.add("download_lamp", {"asset_id": "lamp_01", "type": "models"}, [])
graph.add("setup_scene", {"assets": ["chair", "table", "lamp"]}, 
          ["download_chair", "download_table", "download_lamp"])

results = await graph.execute(client)
```

---

## ⚡ ERROR HANDLING & RETRY LOGIC

### Retry with Exponential Backoff
```python
class ResilientMCPClient:
    def __init__(self, client, max_retries=3, base_delay=1.0):
        self.client = client
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    async def call_with_retry(self, tool_name: str, params: dict):
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                result = await self.client.call_tool(tool_name, params)
                if "error" not in result:
                    return result
                last_error = result["error"]
            except Exception as e:
                last_error = str(e)
            
            if attempt < self.max_retries:
                delay = self.base_delay * (2 ** attempt) + random.uniform(0, 0.1)
                await asyncio.sleep(delay)
        
        raise MCPError(f"Failed after {self.max_retries} retries: {last_error}")
```

### Circuit Breaker Pattern
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failures = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.state = "closed"  # closed, open, half-open
        self.last_failure_time = None
    
    async def call(self, func, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
            else:
                raise CircuitOpenError("Circuit breaker open")
        
        try:
            result = await func()
            if self.state == "half-open":
                self.state = "closed"
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.failure_threshold:
                self.state = "open"
            raise
```

---

## 🔒 SECURITY & SANDBOXING

### Blender-MCP Safe Mode Configuration
```python
# Server-side safe mode enforcement
class SafeModeValidator:
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
    
    @classmethod
    def validate_code(cls, code: str) -> tuple[bool, str]:
        tree = ast.parse(code)
        
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
        
        return True, "OK"
```

### Client-Side Permission Model
```python
class PermissionManager:
    PERMISSIONS = {
        "read_scene": ["get_scene_info", "get_object_info", "get_viewport_screenshot"],
        "modify_scene": ["create_object", "modify_object", "delete_object"],
        "materials": ["set_material", "create_material"],
        "assets": ["download_polyhaven_asset", "search_polyhaven_assets"],
        "ai_generation": ["create_rodin_job", "poll_rodin_job_status"],
        "code_execution": ["execute_blender_code"],
        "admin": ["get_addon_info", "set_telemetry_consent"],
    }
    
    def __init__(self, allowed_roles: list[str]):
        self.allowed = set()
        for role in allowed_roles:
            self.allowed.update(self.PERMISSIONS.get(role, []))
    
    def check(self, tool_name: str) -> bool:
        return tool_name in self.allowed
    
    def filter_tools(self, all_tools: list) -> list:
        return [t for t in all_tools if t["name"] in self.allowed]
```

---

## 📊 OBSERVABILITY & LOGGING

### Structured Logging for MCP
```python
import structlog

logger = structlog.get_logger()

class ObservableMCPClient:
    def __init__(self, client):
        self.client = client
        self.logger = structlog.get_logger("mcp.client")
    
    async def call_tool(self, tool_name: str, params: dict):
        start = time.time()
        request_id = uuid.uuid4().hex[:8]
        
        self.logger.info("mcp_request", 
            request_id=request_id,
            tool=tool_name,
            params_keys=list(params.keys())
        )
        
        try:
            result = await self.client.call_tool(tool_name, params)
            duration = time.time() - start
            
            self.logger.info("mcp_response",
                request_id=request_id,
                tool=tool_name,
                duration_ms=round((time.time() - start) * 1000, 2),
                success="error" not in result
            )
            return result
        except Exception as e:
            self.logger.error("mcp_error",
                request_id=request_id,
                tool=tool_name,
                error=str(e),
                duration_ms=round((time.time() - start) * 1000, 2)
            )
            raise
```

---

## 🧪 TESTING MCP TOOLS

### Unit Test Framework
```python
import pytest
from unittest.mock import AsyncMock, MagicMock

class TestMCPTools:
    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        client.call_tool = AsyncMock()
        return client
    
    @pytest.mark.asyncio
    async def test_create_object(self, mock_client):
        mock_client.call_tool.return_value = {
            "name": "Cube", "type": "MESH", "location": [0, 0, 0]
        }
        
        result = await create_object(mock_client, "CUBE", "TestCube", [1, 2, 3])
        
        assert result["name"] == "TestCube"
        mock_client.call_tool.assert_called_once_with(
            "create_object",
            {"entity_type": "CUBE", "name": "TestCube", "location": [1, 2, 3]}
        )
    
    @pytest.mark.asyncio
    async def test_retry_on_failure(self, mock_client):
        mock_client.call_tool.side_effect = [
            Exception("Network error"),
            {"name": "Cube", "type": "MESH"}
        ]
        
        client = ResilientMCPClient(mock_client, max_retries=2)
        result = await client.call_with_retry("create_object", {})
        
        assert result["name"] == "Cube"
        assert mock_client.call_tool.call_count == 2

# Integration test with real Blender
@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_scene_creation(blender_mcp_client):
    """Requires running Blender with MCP server"""
    result = await blender_mcp_client.call_tool("get_scene_info", {})
    assert "objects" in result
    assert isinstance(result["objects"], list)
```

---

## 🔗 LINKS

- **MCP Spec:** https://modelcontextprotocol.io/
- **FastMCP:** https://github.com/jlowin/fastmcp
- **Blender-MCP:** https://github.com/ahujasid/blender-mcp
- **GenesisCore:** https://github.com/AIGODLIKE/GenesisCore
- **Structlog:** https://www.structlog.org/

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/mcp_advanced/streaming_tools.md` |
| Russian | `multilang/ru/mcp_advanced/streaming_tools.md` |