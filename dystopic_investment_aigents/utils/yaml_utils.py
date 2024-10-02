from adalflow import OpenAIClient
import yaml


class YAMLUtils:
    @staticmethod
    def openai_client_constructor(loader, node):
        return OpenAIClient()

    @classmethod
    def register_constructors(cls):
        yaml.SafeLoader.add_constructor('!openai_client', cls.openai_client_constructor)

    @staticmethod
    def safe_load(stream):
        YAMLUtils.register_constructors()
        return yaml.safe_load(stream)