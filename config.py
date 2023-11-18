
import os
from dynaconf import Dynaconf

env = os.environ.get("ENV")
settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=[f'conf/settings.{env}.yaml'],
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
