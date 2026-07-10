#!/usr/bin/env node
/**
 * nanobot WhatsApp Bridge
 * 
 * This bridge connects WhatsApp Web to nanobot's Python backend
 * via WebSocket. It handles authentication, message forwarding,
 * and reconnection logic.
 * 
 * Usage:
 *   npm run build && npm start
 *   
 * Or with custom settings:
 *   BRIDGE_PORT=3001 AUTH_DIR=~/.nanobot/whatsapp npm start
 */

// Polyfill crypto for Baileys in ESM
import { webcrypto } from 'crypto';
if (!globalThis.crypto) {
  (globalThis as any).crypto = webcrypto;
}

import { BridgeServer } from './server.js';
import { dirname, join, resolve } from 'path';
import { fileURLToPath } from 'url';

const PORT = parseInt(process.env.BRIDGE_PORT || '3001', 10);
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const repoRoot = resolve(__dirname, '..', '..', '..');
const AUTH_DIR = process.env.AUTH_DIR || process.env.XIAOMIAO_AGENT_CACHE_DIR || join(repoRoot, '.cache', 'agent', 'nanobot', 'whatsapp-auth');
const TOKEN = process.env.BRIDGE_TOKEN?.trim();

if (!TOKEN) {
  console.error('BRIDGE_TOKEN is required. Start the bridge via nanobot so it can provision a local secret automatically.');
  process.exit(1);
}

console.log('🐈 nanobot WhatsApp Bridge');
console.log('========================\n');

const server = new BridgeServer(PORT, AUTH_DIR, TOKEN);

// Handle graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n\nShutting down...');
  await server.stop();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  await server.stop();
  process.exit(0);
});

// Start the server
server.start().catch((error) => {
  console.error('Failed to start bridge:', error);
  process.exit(1);
});
