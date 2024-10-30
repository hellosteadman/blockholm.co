from django.apps import AppConfig, apps
from django.utils.module_loading import module_has_submodule
from importlib import import_module


class OEmbedConfig(AppConfig):
    name = 'sidekick.oembed'

    def ready(self):
        for config in apps.get_app_configs():
            if config.name == self.name:
                continue

            name = '%s.oembed' % config.name

            try:
                import_module(name)
            except ImportError:
                if module_has_submodule(config.name, 'oembed'):
                    raise  # pragma: no cover
