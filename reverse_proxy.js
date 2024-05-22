// proxy-server.js

const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const yargs = require('yargs');

// Global array of backend servers
const backendServers = [
  'http://127.0.0.1:7101',
  'http://127.0.0.1:7102',
  'http://127.0.0.1:7103',
  'http://127.0.0.1:7104',
  'http://127.0.0.1:7105',
  // Add more backend server URLs as needed
];

// Get the public port from command-line arguments
const argv = yargs(process.argv.slice(2)).argv;
const port = argv.port || 7100;

const app = express();

// Middleware to select a backend server
app.use((req, res, next) => {
  // Simple load balancing: Round Robin or any other algorithm
  const target = backendServers[Math.floor(Math.random() * backendServers.length)];

  // Attach the chosen target to the request object
  req.target = target;
  next();
});

// Proxy middleware
app.use(
  '/',
  createProxyMiddleware({
    target: '', // This value will be overridden by the middleware
    router: (req) => req.target,
    changeOrigin: true,
  })
);

// Start the proxy server
app.listen(port, '127.0.0.1', () => {
  console.log(`Reverse proxy server is running on http://127.0.0.1:${port}`);
});
