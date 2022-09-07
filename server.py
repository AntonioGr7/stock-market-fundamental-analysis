from engine.analysis_engine import AnalysisEngine
import os
from service_core.server.server import RestServer
from service_core.config.load_configuration import ConfigurationLoader
from controller.controller import router



if __name__ == '__main__':
    path = os.getcwd() + "/settings/config.yaml"
    configuration = ConfigurationLoader.load(path)
    server = RestServer(name=configuration.core.server.name,
                        description=configuration.core.server.description,
                        prefix=configuration.core.server.prefix,
                        apikey=configuration.core.auth.xapikey)
    print(router.routes)
    server.include_router(router)
    server.run(host=configuration.core.server.host,
               port=configuration.core.server.port,
               log_level=configuration.core.log_level)

