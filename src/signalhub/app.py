import asyncio
import signal
import sys
import logging
from aiosmtpd.controller import Controller
from .config import load_config
from .handler import Handler
from .health import start_health_server


def main():
    config = load_config()
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    loop = asyncio.get_event_loop()

    handler = Handler(config)
    controller = Controller(
        handler,
        hostname=config.listen_host,
        port=config.listen_port,
        require_starttls=config.enable_starttls,
        auth_required=not config.allow_nonauth,
        authenticator=handler.authenticator if not config.allow_nonauth else None,
        tls_context=handler.tls_context if config.enable_starttls else None,
    )
    controller.start()

    health_task = loop.create_task(start_health_server(config))

    def shutdown():
        logging.info('{"event":"shutdown","status":"initiated"}')
        controller.stop()
        health_task.cancel()
        loop.stop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        shutdown()
    finally:
        loop.close()
        logging.info('{"event":"shutdown","status":"complete"}')

if __name__ == "__main__":
    main()
