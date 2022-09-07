from dependency_injector import containers, providers
from service_core.utils.http_client.http_client import HTTPClient
from service_core.config.log_configuration import setup_logging

class Core(containers.DeclarativeContainer):
    config = providers.Configuration()

    logging = providers.Resource(
        setup_logging,
        log_level=config.core.log_level
    )

class Gateways(containers.DeclarativeContainer):
    config = providers.Configuration()

    http_client = providers.Singleton(
        HTTPClient,
        url=config.docanalyzes.url,
        apikey=config.docanalyzes.apikey
    )

class Application(containers.DeclarativeContainer):
    config = providers.Configuration()

    core = providers.Container(
        Core,
        config=config,
    )

    gateways = providers.Container(
        Gateways,
        config=config.gateways,
    )
