from rest_framework.viewsets import ModelViewSet, ViewSetMixin
from .models import Lesson
from rest_framework import permissions, generics, mixins
from .serializers import LessonListSerializer, LessonDetailSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from lesson_impressions.serializers import LikeSerializer, DislikeSerializer, CommentSerializer, CommentListSerializer
from rest_framework.response import Response
from lesson_impressions.models import Like, Dislike, Comment
from question.serializers import QuestionSerializer, CreateQuestionSerializer
from course.models import Course


class StandardResultPagination(PageNumberPagination):
    page_size = 1
    page_query_param = 'lesson'


class LessonViewSet(ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonDetailSerializer
    pagination_class = StandardResultPagination

    def get_permissions(self):
        if self.action in ['destroy', 'update', 'create', 'partial_update']:
            return permissions.IsAdminUser(),
        return permissions.IsAuthenticated(),

    def list(self, request, *args, **kwargs):
        course_id = request.GET.get('course_id')
        user = request.user
        try:
            course = Course.objects.get(id=course_id)
        except:
            return Response('Either no course_id was provided or course with that id doesnt exist!', status=400)
        lessons = self.get_queryset().filter(course=course).all().order_by('created_at')
        page = self.paginate_queryset(lessons)
        if page is not None:
            serializer = LessonDetailSerializer(instance=page, many=True, context={'owner': user})
            return self.get_paginated_response(serializer.data)
        return Response('smth went wrong in listing')

    @action(methods=['GET', 'POST'], detail=True)
    def likes(self, request, pk):
        lesson = self.get_object()
        user = request.user
        if request.method == 'GET':
            likes = lesson.likes.all()
            serializer = LikeSerializer(instance=likes, many=True)
            return Response(serializer.data, status=200)
        elif request.method == 'POST':
            if user.likes.filter(lesson=lesson).exists():
                user.likes.filter(lesson=lesson).delete()
                return Response('Like was removed', status=204)
            Like.objects.create(owner=user, lesson=lesson)
            return Response('Like was added', status=201)

    @action(methods=['GET', 'POST'], detail=True)
    def dislikes(self, request, pk):
        lesson = self.get_object()
        user = request.user
        if request.method == 'GET':
            dislikes = lesson.dislikes.all()
            serializer = DislikeSerializer(instance=dislikes, many=True)
            return Response(serializer.data, status=200)
        elif request.method == 'POST':
            if user.dislikes.filter(lesson=lesson).exists():
                user.dislikes.filter(lesson=lesson).delete()
                return Response('Dislike was removed', status=204)
            Dislike.objects.create(owner=user, lesson=lesson)
            return Response('Dislike was added', status=201)

    @action(methods=['GET', 'POST', 'DELETE'], detail=True)
    def questions(self, request, pk):
        lesson = self.get_object()
        user = request.user
        if self.request.method == 'GET':
            questions = lesson.questions.all()
            serializer = QuestionSerializer(instance=questions, many=True, context={'owner': user})
            return Response(serializer.data, status=200)
        elif self.request.method == 'POST':
            if lesson.questions.all().exists():
                return Response('This lesson already has a question', status=400)
            serializer = CreateQuestionSerializer(data=request.data, context={'lesson': lesson})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response('Question created!', status=201)
        elif self.request.method == 'DELETE':
            if not lesson.questions.all().exists():
                return Response('This lesson doesnt have any questions!', status=400)
            lesson.questions.get(lesson=lesson).delete()
            return Response('Question deleted', status=204)

    @action(methods=['GET', 'POST', 'DELETE'], detail=True)
    def comments(self, request, pk):
        lesson = self.get_object()
        user = request.user
        if request.method == 'GET':
            try:
                comment_id = request.GET.get('comment_id')
                return Response(CommentSerializer(Comment.objects.get(pk=comment_id)).data, status=200)
            except:
                comments = lesson.comments.all().order_by('created_at')
                serializer = CommentListSerializer(instance=comments, many=True)
                return Response(serializer.data, status=200)

        elif request.method == 'POST':
            serializer = CommentSerializer(data=request.data, context={'lesson': lesson, 'owner': user})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=201)

        elif request.method == 'DELETE':
            comment_id = self.request.query_params.get('comment_id')
            comment = lesson.comments.filter(lesson=lesson, pk=comment_id)
            if comment.exists():
                comment.delete()
                return Response('Successfully deleted', status=204)
        return Response('Not found', status=404)