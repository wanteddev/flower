import logging

import prometheus_client

from ..views import BaseHandler

logger = logging.getLogger(__name__)


class Metrics(BaseHandler):
    async def get(self):
        self.write(prometheus_client.generate_latest())
        self.set_header("Content-Type", "text/plain")

    async def delete(self):
        offline_workers = []
        for worker_name, worker in self.application.events.state.workers.items():
            if not worker.alive:
                offline_workers.append(worker_name)
        logger.info("offline workers: %s, %d", offline_workers, len(offline_workers))
        for worker_name in offline_workers:
            for collector in prometheus_client.REGISTRY._collector_to_names.keys():
                if hasattr(collector, '_metrics') and hasattr(collector._metrics, 'keys'):
                    for metric_key in list(collector._metrics.keys()):
                        if isinstance(metric_key, tuple):
                            if worker_name in metric_key:
                                try:
                                    del collector._metrics[metric_key]
                                except KeyError:
                                    pass
                        elif metric_key == worker_name:
                            try:
                                del collector._metrics[metric_key]
                            except KeyError:
                                pass
        self.write("OK")
        self.set_header("Content-Type", "text/plain")

class Healthcheck(BaseHandler):
    async def get(self):
        self.write("OK")

