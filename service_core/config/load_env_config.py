import os
from envyaml import EnvYAML

def get_env(key, default_value):
    return os.getenv(key, default_value)


def load_yamlenv(path="/settings/config.yaml", override=True):
    if os.path.exists(path):
        # read file env.yaml and parse config
        env = EnvYAML(path)

        for k, v in vars(env)["_EnvYAML__cfg"].items():
            if k in os.environ and not override:
                continue
            if v is not None:
                os.environ[k] = str(v)
