function normalizeMcpUrl(u) {
  try {
    if (!u) return null;
    const parsed = new URL(u);
    // Prefer loopback IP for in-container access
    const host = (parsed.hostname === 'localhost') ? '127.0.0.1' : parsed.hostname;
    let pathname = parsed.pathname || '';
    if (pathname === '' || pathname === '/') pathname = '/sse';
    return `${parsed.protocol}//${host}:${parsed.port || '80'}${pathname}`;
  } catch {
    return null;
  }
}
import express from 'express';
import process from 'process';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { spawn } from 'node:child_process';

// Environment
const PORT = process.env.PORT || 8080;
const PLAYWRIGHT_ARGS = (process.env.PLAYWRIGHT_ARGS || '').split(' ').filter(Boolean);
// Port for local MCP host HTTP server
const MCP_PORT = Number(process.env.MCP_PORT || 8931);

// MCP Client setup (single persistent connection)
const client = new Client(
  { name: 'playwright-mcp-relay', version: '0.1.0' },
  { capabilities: { experimental: {} } }
);

async function preflightHelp() {
  try {
    const { spawn } = await import('node:child_process');
    const cliPath = '/usr/src/app/node_modules/@playwright/mcp/cli.js';
    await new Promise((resolve) => {
      const proc = spawn('node', [cliPath, '--help'], { cwd: '/usr/src/app' });
      let out = '';
      proc.stdout.on('data', (d) => { out += d.toString(); });
      proc.stderr.on('data', (d) => { out += d.toString(); });
      proc.on('exit', (code) => {
        lastHelp = `help exit=${code} output=\n${out.substring(0, 2000)}`;
        lastStderr.push(`[preflight] ${lastHelp}`);
        if (lastStderr.length > 50) lastStderr.shift();
        resolve();
      });
    });
  } catch (e) {
    const msg = `[preflight] help failed: ${String(e)}`;
    console.error(msg);
    lastStderr.push(msg);
    if (lastStderr.length > 50) lastStderr.shift();
  }
}
let transport = null;
let lastError = null;
let lastStderr = [];
let lastMcpUrl = null;
let lastHelp = null;
async function preflightCheck() {
  try {
    const { spawn } = await import('node:child_process');
    const cliPath = '/usr/src/app/node_modules/@playwright/mcp/cli.js';
    console.log('[preflight] checking CLI at', cliPath);
    await new Promise((resolve) => {
      const proc = spawn('node', [cliPath, '--version'], { cwd: '/usr/src/app' });
      let out = '';
      proc.stdout.on('data', (d) => { out += d.toString(); });
      proc.stderr.on('data', (d) => { out += d.toString(); });
      proc.on('exit', (code) => {
        const msg = `[preflight] version exit=${code} output=\n${out}`;
        console.log(msg);
        lastStderr.push(msg);
        if (lastStderr.length > 20) lastStderr.shift();
        resolve();
      });
    });
  } catch (e) {
    const msg = `[preflight] failed: ${String(e)}`;
    console.error(msg);
    lastStderr.push(msg);
    if (lastStderr.length > 20) lastStderr.shift();
  }
}

let connected = false;
let connecting = false;

async function connectLoop() {
  if (connecting || connected) return;
  connecting = true;
  const baseDelay = 3000;
  let attempt = 0;
  while (!connected) {
    try {
      if (!transport) {
        // Start official Playwright MCP HTTP server via local CLI
        const cliPath = '/usr/src/app/node_modules/@playwright/mcp/cli.js';
        const hostArgs = [cliPath, '--port', String(MCP_PORT), ...PLAYWRIGHT_ARGS];
        console.log('Starting Playwright MCP via local CLI:', 'node', hostArgs.join(' '));
        const child = spawn('node', hostArgs, {
          cwd: '/usr/src/app',
          env: {
            ...process.env,
            PLAYWRIGHT_BROWSERS_PATH: '/ms-playwright',
            HOME: '/tmp',
            XDG_CACHE_HOME: '/tmp',
          },
          stdio: ['ignore', 'pipe', 'pipe'],
        });
        child.stdout.on('data', (d) => {
          const msg = d.toString();
          console.log('[playwright-mcp][stdout]', msg.trim());
          lastStderr.push(`[stdout] ${msg}`);
          if (lastStderr.length > 50) lastStderr.shift();
          const urlMatch = msg.match(/https?:\/\/[^\s]+/);
          if (urlMatch) {
            const normalized = normalizeMcpUrl(urlMatch[0]);
            if (normalized) lastMcpUrl = normalized;
          }
        });
        child.stderr.on('data', (d) => {
          const msg = d.toString();
          console.error('[playwright-mcp][stderr]', msg.trim());
          lastStderr.push(`[stderr] ${msg}`);
          if (lastStderr.length > 50) lastStderr.shift();
        });
        child.on('exit', (code, signal) => {
          console.error(`[playwright-mcp] exited code=${code} signal=${signal}`);
          connected = false;
          transport = null;
        });

        // Polyfill EventSource and connect via SSE only after host is listening
        const EventSourceModule = await import('eventsource');
        const ES = (EventSourceModule && (EventSourceModule.default || EventSourceModule.EventSource)) || EventSourceModule;
        // @ts-ignore
        globalThis.EventSource = ES;
        const { SSEClientTransport } = await import('@modelcontextprotocol/sdk/client/sse.js');
        // Wait up to 10s for host to announce the listening URL
        let waitMs = 0;
        while (!lastMcpUrl && waitMs < 10000) {
          await new Promise(r => setTimeout(r, 250));
          waitMs += 250;
        }
        // Ensure server had time to bind even if it didn't print URL
        await new Promise(r => setTimeout(r, 3000));
        const url = normalizeMcpUrl(lastMcpUrl) || `http://127.0.0.1:${MCP_PORT}/sse`;
        console.log('Connecting to local MCP SSE:', url);
        transport = new SSEClientTransport(url);
      }
      await preflightCheck();
      await preflightHelp();
      // Give the child process a short moment to initialize before connect
      await new Promise(r => setTimeout(r, 800));
      console.log('MCP client connecting...');
      await client.connect(transport);
      console.log('MCP client connected, sending ping...');
      await client.ping();
      connected = true;
      console.log('Connected to Playwright MCP via local HTTP SSE.');
      break;
    } catch (err) {
      attempt += 1;
      const delay = Math.min(baseDelay * Math.pow(2, Math.min(attempt, 5)), 30000);
      lastError = String(err && err.stack ? err.stack : err);
      console.error(`Failed to connect to Playwright MCP (attempt ${attempt}). Retrying in ${delay}ms:`, err);
      // Force respawn on next loop
      transport = null;
      lastMcpUrl = null;
      await new Promise(r => setTimeout(r, delay));
    }
  }
  connecting = false;
}

// Start connection attempts in background
connectLoop();

// Helper to call a tool safely
async function callToolSafe(name, args) {
  // Ensure connection (with simple wait loop if not yet connected)
  if (!connected) await connectLoop();
  let waits = 0;
  while (!connected && waits < 20) {
    await new Promise(r => setTimeout(r, 500));
    waits++;
  }
  if (!connected) throw new Error('MCP connection not established');
  const res = await client.callTool({ name, arguments: args || {} });
  return res;
}

const app = express();
app.use(express.json());

app.get('/', (_req, res) => {
  res.status(200).json({ ok: true, service: 'playwright-mcp-relay' });
});

app.get('/healthz', (_req, res) => {
  res.status(200).json({ status: 'ok' });
});

app.get('/status', (_req, res) => {
  res.status(200).json({ connected, connecting, transport: 'sse-local', args: PLAYWRIGHT_ARGS, lastError, lastStderr, lastMcpUrl, lastHelp });
});

// Initialize session (optional explicit init)
app.post('/initialize', async (_req, res) => {
  try {
    // No-op: SDK handled handshake on connect. Reply success so callers can gate on it.
    res.status(200).json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: String(e) });
  }
});

app.post('/navigate', async (req, res) => {
  try {
    const { url } = req.body || {};
    if (!url || !/^https?:\/\//.test(url)) return res.status(400).json({ error: 'Invalid url' });
    const result = await callToolSafe('browser_navigate', { url });
    res.status(200).json(result);
  } catch (e) {
    res.status(500).json({ error: String(e) });
  }
});

app.post('/snapshot', async (_req, res) => {
  try {
    const result = await callToolSafe('browser_snapshot', {});
    res.status(200).json(result);
  } catch (e) {
    res.status(500).json({ error: String(e) });
  }
});

app.post('/click', async (req, res) => {
  try {
    const { ref, element, doubleClick, button, modifiers } = req.body || {};
    if (!ref || !element) return res.status(400).json({ error: 'Missing ref or element' });
    const result = await callToolSafe('browser_click', { ref, element, doubleClick, button, modifiers });
    res.status(200).json(result);
  } catch (e) {
    res.status(500).json({ error: String(e) });
  }
});

app.post('/type', async (req, res) => {
  try {
    const { ref, element, text, submit, slowly } = req.body || {};
    if (!ref || !element || typeof text !== 'string') return res.status(400).json({ error: 'Missing ref, element or text' });
    const result = await callToolSafe('browser_type', { ref, element, text, submit, slowly });
    res.status(200).json(result);
  } catch (e) {
    res.status(500).json({ error: String(e) });
  }
});

app.listen(PORT, () => {
  console.log(`MCP Relay listening on :${PORT}`);
});
