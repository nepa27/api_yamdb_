"""
Сериализаторы для взаимодействия с моделями в API.

Этот модуль содержит сериализаторы для взаимодействия с моделями,
такими как Category, Genre, Title, Comment и Review,
в рамках API Django REST Framework.

"""
from datetime import date

from rest_framework import serializers

from reviews.models import Category, Genre, Title, Comment, Review


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        """Класс Meta."""

        model = Category
        fields = (
            'name',
            'slug'
        )


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        """Класс Meta."""

        model = Genre
        fields = (
            'name',
            'slug'
        )


class ReadTitleSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения информации о произведении (Title)."""

    genre = GenreSerializer(many=True,)
    category = CategorySerializer()
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        """Класс Meta."""

        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )
        model = Title
        read_only_fields = fields


class WriteTitleSerializer(serializers.ModelSerializer):
    """Сериализатор для записи информации о произведении (Title)."""

    genre = serializers.SlugRelatedField(
        many=True, slug_field='slug', queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        """Класс Meta."""

        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category'
        )
        model = Title


    def validate_year(self, value):
        """Проверяет, что год не превышает текущий год."""
        if value > date.today().year:
            raise serializers.ValidationError(
                f"""Введенный год ({value})
                не может быть больше текущего ({date.today().year})."""
            )
        return value


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения и записи информации о комментарии (Comment)."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    pub_date = serializers.DateTimeField(read_only=True)

    class Meta:
        """Класс Meta."""

        fields = (
            'id',
            'text',
            'author',
            'pub_date'
        )
        model = Comment


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения и записи информации о отзыве (Review)."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    pub_date = serializers.DateTimeField(read_only=True)

    class Meta:
        """Класс Meta."""

        fields = (
            'id',
            'text',
            'author',
            'score',
            'pub_date'
        )
        model = Review

    def validate_score(self, value):
        """Валидация оценки."""
        if value < 1 or value > 10:
            raise serializers.ValidationError('Оценка должна быть от 1 до 10.')
        return value

    def validate(self, data):
        """
        Проверка валидности данных.

        Проверяет, что пользователь не оставляет
        повторные отзывы для одного произведения.
        """
        title_id = self.context.get('view').kwargs.get('title_id')
        if self.context['request'].method == 'POST' and Review.objects.filter(
            title=title_id, author=self.context['request'].user
        ).exists():
            raise serializers.ValidationError(
                'Отзыв на это произведение уже оставлен!'
            )
        return data
