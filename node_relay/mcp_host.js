import http from 'http';
import process from 'process';
import pkg from '@playwright/mcp';
const { createConnection } = pkg;
import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js';

const PORT = Number(process.env.MCP_PORT || 8931);

async function handler(req, res) {
  try {
    // Only accept the MCP SSE path
    if (!req.url.startsWith('/messages')) {
      res.statusCode = 404;
      res.end('Not Found');
      return;
    }

    // Create a new Playwright MCP connection per incoming stream
    const connection = await createConnection({
      browser: {
        channel: 'chromium',
        launchOptions: {
          headless: true,
          args: ['--no-sandbox'],
        },
      },
    });

    const transport = new SSEServerTransport('/messages', res);
    await connection.server.connect(transport);
  } catch (e) {
    console.error('[mcp-host] error handling request:', e);
    try { res.statusCode = 500; res.end(String(e)); } catch {}
  }
}

const server = http.createServer((req, res) => {
  handler(req, res);
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`[mcp-host] listening on http://127.0.0.1:${PORT}/messages`);
});
