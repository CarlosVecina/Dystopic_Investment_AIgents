from adalflow import OpenAIClient
import yaml

from dystopic_investment_aigents.utils.model_client_utils import OpenAIClientTraceable


class YAMLUtils:
    @staticmethod
    def openai_client_constructor(loader, node):
        return OpenAIClient()
    
    @staticmethod
    def openai_client_traceable_constructor(loader, node):
        if not hasattr(YAMLUtils, '_openai_client_traceable_instance'):
            YAMLUtils._openai_client_traceable_instance = OpenAIClientTraceable()
        return YAMLUtils._openai_client_traceable_instance

    @classmethod
    def register_constructors(cls):
        yaml.SafeLoader.add_constructor('!openai_client', cls.openai_client_constructor)
        yaml.SafeLoader.add_constructor('!openai_client_traceable', cls.openai_client_traceable_constructor)

    @staticmethod
    def safe_load(stream):
        YAMLUtils.register_constructors()
        return yaml.safe_load(stream)