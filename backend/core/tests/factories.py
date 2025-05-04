import factory
from rest_framework.test import APIClient


class APIClientFactory(factory.Factory):
    class Meta:
        model = APIClient

    @factory.post_generation
    def user(self, create, extracted ,**kwargs):
        if not create:
            return
        if extracted:
            self.force_authenticate(extracted)