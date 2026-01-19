"""Backend entry point for PyInstaller bundling."""
import sys
import socket
import signal
import logging
import argparse
from pathlib import Path

# Emit early signal BEFORE heavy imports - helps Electron detect startup
print("PPTAgent backend initializing...", flush=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('PPTAgent-Backend')

DEFAULT_PORT = 7861
MAX_PORT_ATTEMPTS = 10


def find_available_port(start_port: int = DEFAULT_PORT, max_attempts: int = MAX_PORT_ATTEMPTS) -> int:
    """Find an available port starting from start_port.

    Args:
        start_port: Port number to start checking from.
        max_attempts: Maximum number of ports to try.

    Returns:
        Available port number.

    Raises:
        RuntimeError: If no available port found within max_attempts.
    """
    for offset in range(max_attempts):
        port = start_port + offset
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            logger.warning(f'Port {port} is in use, trying next...')
    raise RuntimeError(f'No available port found in range {start_port}-{start_port + max_attempts - 1}')

def signal_handler(sig, frame):
    logger.info('Shutdown signal received')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='PPTAgent Backend Server')
    parser.add_argument('--port', type=int, default=None, help='Port to run the server on')
    args = parser.parse_args()

    from deeppresenter.utils.log import log_startup

    log_startup("PPTAgent Backend")

    logger.info('Starting PPTAgent backend...')
    from webui import ChatDemo
    from deeppresenter.utils.constants import WORKSPACE_BASE

    # Use provided port or find available one
    port = args.port if args.port else find_available_port()
    chat_demo = ChatDemo()
    demo = chat_demo.create_interface()

    logger.info(f'Launching Gradio server on localhost:{port}')
    demo.launch(
        debug=False,
        server_name='localhost',
        server_port=port,
        share=False,
        max_threads=16,
        allowed_paths=[WORKSPACE_BASE],
    )

if __name__ == '__main__':
    main()
