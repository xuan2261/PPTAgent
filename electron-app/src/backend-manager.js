const { spawn } = require('child_process');
const path = require('path');
const net = require('net');
const fs = require('fs');
const kill = require('tree-kill');
const { app } = require('electron');

const DEFAULT_PORT = 7861;
const MAX_PORT_ATTEMPTS = 10;

/**
 * Check if a port is available.
 * @param {number} port - Port to check
 * @returns {Promise<boolean>} - True if port is available
 */
function isPortAvailable(port) {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.once('error', () => resolve(false));
    server.once('listening', () => {
      server.close();
      resolve(true);
    });
    server.listen(port, 'localhost');
  });
}

/**
 * Find an available port starting from startPort.
 * @param {number} startPort - Port to start checking from
 * @param {number} maxAttempts - Maximum ports to try
 * @returns {Promise<number>} - Available port number
 */
async function findAvailablePort(startPort = DEFAULT_PORT, maxAttempts = MAX_PORT_ATTEMPTS) {
  for (let offset = 0; offset < maxAttempts; offset++) {
    const port = startPort + offset;
    if (await isPortAvailable(port)) {
      return port;
    }
    console.log(`Port ${port} is in use, trying next...`);
  }
  throw new Error(`No available port found in range ${startPort}-${startPort + maxAttempts - 1}`);
}

class BackendManager {
  constructor() {
    this.process = null;
    this.port = DEFAULT_PORT;
    this.isReady = false;
  }

  getBackendPath() {
    if (app.isPackaged) {
      return path.join(process.resourcesPath, 'backend', 'backend.exe');
    }
    return path.join(__dirname, '../../python-dist/backend.exe');
  }

  start() {
    return new Promise(async (resolve, reject) => {
      try {
        this.port = await findAvailablePort();
        console.log(`Using port: ${this.port}`);
      } catch (err) {
        reject(err);
        return;
      }

      const backendPath = this.getBackendPath();
      console.log(`Starting backend: ${backendPath}`);

      // Check if backend executable exists before spawning
      if (!fs.existsSync(backendPath)) {
        const isDev = !app.isPackaged;
        const helpMsg = isDev
          ? 'Run "pyinstaller backend.spec --clean && cp dist/backend.exe python-dist/" to build it.'
          : 'Please reinstall the application or contact support.';
        reject(new Error(`Backend not found: ${backendPath}\n\n${helpMsg}`));
        return;
      }

      this.process = spawn(backendPath, ['-u', '--port', this.port.toString()], {
        stdio: ['pipe', 'pipe', 'pipe'],
        windowsHide: true,
      });

      const timeout = setTimeout(() => {
        reject(new Error('Backend startup timeout (60s)'));
      }, 60000);

      this.process.stdout.on('data', (data) => {
        const output = data.toString();
        console.log(`[Backend] ${output}`);

        // Log initialization progress (don't resolve yet)
        if (output.includes('initializing')) {
          console.log('Backend is initializing...');
          return;
        }

        // Match dynamic port pattern - support multiple Gradio output formats
        const portMatch = output.match(/localhost:(\d+)/);
        const isReady =
          output.includes('Running on') ||           // Gradio standard
          output.includes('Launching Gradio') ||     // Custom log
          output.includes('local URL:') ||           // Gradio URL format
          portMatch;

        if (isReady) {
          if (portMatch) {
            this.port = parseInt(portMatch[1], 10);
          }
          clearTimeout(timeout);
          this.isReady = true;
          resolve(this.port);
        }
      });

      this.process.stderr.on('data', (data) => {
        console.error(`[Backend Error] ${data}`);
      });

      this.process.on('error', (err) => {
        clearTimeout(timeout);
        reject(new Error(`Failed to start backend: ${err.message}`));
      });

      this.process.on('exit', (code) => {
        console.log(`Backend exited with code ${code}`);
        this.isReady = false;
      });
    });
  }

  async stop() {
    if (this.process) {
      return new Promise((resolve) => {
        kill(this.process.pid, 'SIGTERM', (err) => {
          if (err) console.error('Error killing backend:', err);
          this.process = null;
          this.isReady = false;
          resolve();
        });
      });
    }
  }
}

module.exports = BackendManager;
