const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const yargs = require('yargs');

// Parse command-line arguments
const argv = yargs(process.argv.slice(2))
  .option('port', {
    alias: 'p',
    type: 'number',
    description: 'Public port for the proxy server',
    default: 7100,
    demandOption: true,
  })
  .option('appServerBasePort', {
    alias: 'b',
    type: 'number',
    default: 7101,
    description: 'Base port number for the backend servers',
    demandOption: true,
  })
  .option('num', {
    alias: 'n',
    type: 'number',
    description: 'Number of backend servers',
    demandOption: true,
  })
  .argv;

const port = argv.port;
const appServerBasePort = argv.appServerBasePort;
const numServers = argv.num;

// Generate the list of backend servers
const backendServers = [];
for (let i = 0; i < numServers; i++) {
  backendServers.push(`http://127.0.0.1:${appServerBasePort + i}`);
}

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
  console.log('Backend servers:', backendServers);
});
