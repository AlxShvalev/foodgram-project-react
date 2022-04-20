from rest_framework import mixins, viewsets


class CreateDestroyModelViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass
