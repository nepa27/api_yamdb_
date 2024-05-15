"""
Модуль, содержащий View для обработки запросов к API.

Этот модуль содержит классы View, предназначенных для обработки HTTP-запросов
к API для моделей Category, Genre, Title, Comment и Review.
Каждый класс View предоставляет функциональность для выполнения операций CRUD
(Create, Retrieve, Update, Delete) с соответствующей моделью.
"""
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import SAFE_METHODS

from api.viewsets import ListCreateDestroyViewSet
from api.filters import TitleFilter
from api.serializers import (
    CategorySerializer,
    GenreSerializer,
    ReadTitleSerializer,
    WriteTitleSerializer,
    CommentSerializer,
    ReviewSerializer
)
from api.permissions import (
    AdminOrReadOnlyPermission,
    AdminModeratorAuthorPermission
)
from reviews.models import Category, Genre, Title, Review, Comment


class CategoryViewSet(ListCreateDestroyViewSet):
    """
    View для обработки запросов к модели Category.

    Позволяет выполнять операции CRUD с экземплярами модели Category.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(ListCreateDestroyViewSet):
    """
    View для обработки запросов к модели Genre.

    Позволяет выполнять операции CRUD с экземплярами модели Genre.
    """

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(ModelViewSet):
    """
    View для обработки запросов к модели Title.

    Позволяет выполнять операции CRUD с экземплярами модели Title.
    Поддерживает фильтрацию, пагинацию и аннотации среднего рейтинга.
    """

    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')
    ).order_by(*Title._meta.ordering)
    permission_classes = (AdminOrReadOnlyPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        """
        Получение класса сериализатора.

        Возвращает класс сериализатора в зависимости от метода запроса.
        """
        if self.request.method in SAFE_METHODS:
            return ReadTitleSerializer
        return WriteTitleSerializer


class CommentViewSet(ModelViewSet):
    """
    View для обработки запросов к модели Comment.

    Позволяет выполнять операции CRUD с экземплярами модели Comment.
    """

    queryset = Comment.objects.all()
    permission_classes = (AdminModeratorAuthorPermission,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    serializer_class = CommentSerializer

    def __get_review(self):
        """
        Получение отзыва по его идентификатору.

        Возвращает экземпляр модели Review по его идентификатору
        из параметров запроса.
        """
        return get_object_or_404(Review, pk=self.kwargs['review_id'])

    def get_queryset(self):
        """
        Получение набора запросов для обработки.

        Возвращает набор запросов для обработки запросов к модели Comment. 
        Фильтрует комментарии по отзыву, полученному из параметров запроса. 
        """
        return self.__get_review().comments.all()

    def perform_create(self, serializer):
        """
        Выполнение создания комментария.

        Сохраняет комментарий, автором которого является текущий пользователь,
        и относящийся к отзыву полученному из параметров запроса.
        """
        serializer.save(
            author=self.request.user,
            review=self.__get_review()
        )


class ReviewViewSet(ModelViewSet):
    """
    View для обработки запросов к модели Review.

    Позволяет выполнять операции CRUD с экземплярами модели Review.
    """

    queryset = Review.objects.all()
    permission_classes = (AdminModeratorAuthorPermission,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    serializer_class = ReviewSerializer

    def __get_title(self):
        """
        Получение произведения по его идентификатору.

        Возвращает экземпляр модели Title по его идентификатору
        из параметров запроса.
        """
        return get_object_or_404(Title, pk=self.kwargs['title_id'])

    def get_queryset(self):
        """
        Получение набора запросов для обработки.

        Возвращает набор запросов для обработки запросов к модели Review.
        Фильтрует отзывы по произведению, полученному из параметров запроса.
        """
        return self.__get_title().reviews.all()

    def perform_create(self, serializer):
        """
        Выполнение создания отзыва.

        Сохраняет отзыв, автором которого является текущий пользователь,
        относящийся к произведению полученному из параметров запроса.
        """
        serializer.save(
            author=self.request.user,
            title=self.__get_title()
        )
