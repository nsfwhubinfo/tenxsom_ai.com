#!/usr/bin/env python3
"""
Minimal FastAPI app for MCP server deployment testing
"""

import os
from fastapi import FastAPI

app = FastAPI(title="TenxsomAI MCP Server - Basic", version="1.0.0")

@app.get("/")
def read_root():
    return {
        "service": "TenxsomAI MCP Server", 
        "version": "1.0.0",
        "status": "running",
        "mode": "basic"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "mcp-server"}

@app.get("/api/status")
def api_status():
    return {
        "status": "operational",
        "mode": "basic",
        "environment": {
            "port": os.environ.get("PORT", "8000"),
            "database_connected": False,
            "mcp_enabled": False
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)