from rest_framework import serializers
from .models import Sermon, Devotion, Events, Category, Playlist, Preacher


class SermonSerializer(serializers.ModelSerializer):
    bg_picture_url = serializers.SerializerMethodField()
    audio_file_url = serializers.SerializerMethodField()

    class Meta:
        model = Sermon
        fields = '__all__'

    def get_bg_picture_url(self, obj):
        request = self.context.get('request')
        if obj.bg_picture and request:
            return request.build_absolute_uri(obj.bg_picture.url)
        return None

    def get_audio_file_url(self, obj):
        request = self.context.get('request')
        if obj.audio_file and request:
            return request.build_absolute_uri(obj.audio_file.url)
        return None


class DevotionalsSerializer(serializers.ModelSerializer):
    devotion_thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Devotion
        fields = '__all__'

    def get_devotion_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.devotion_thumbnail and request:
            return request.build_absolute_uri(obj.devotion_thumbnail.url)
        return None


class EventsSerializer(serializers.ModelSerializer):
    event_thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Events
        fields = '__all__'

    def get_event_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.event_thumbnail and request:
            return request.build_absolute_uri(obj.event_thumbnail.url)
        return None


class CategorySerializer(serializers.ModelSerializer):
    category_thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = '__all__'

    def get_category_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.category_thumbnail and request:
            return request.build_absolute_uri(obj.category_thumbnail.url)
        return None

class PreacherSerializer(serializers.ModelSerializer):
    preacher_thumbnail_url = serializers.SerializerMethodField()
    class Meta:
        model = Preacher
        fields = '__all__'

    def get_preacher_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.profile_picture and request:
            return request.build_absolute_uri(obj.profile_picture.url)
        return None

class PlayListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = '__all__'




# class SermonSerializer(serializers.Serializer):
#     title = serializers.CharField()
#     bg_picture_url = serializers.URLField(required=False)
#     audio_file_url = serializers.URLField(required=False)
#     preacher = serializers.CharField()
#     playlist = serializers.ListField()

# class DevotionalsSerializer(serializers.Serializer):
#     title = serializers.CharField()
#     devotion_thumbnail_url = serializers.URLField(required=False)

# class EventsSerializer(serializers.Serializer):
#     title = serializers.CharField()
#     event_thumbnail_url = serializers.URLField(required=False)

# class CategorySerializer(serializers.Serializer):
#     title = serializers.CharField()
#     category_thumbnail_url = serializers.URLField(required=False)


# class PreacherSerializer(serializers.Serializer):
#     name = serializers.CharField()
#     bio = serializers.CharField()
#     profile_picture_url = serializers.URLField(required=False)
#     social_links = serializers.JSONField(required=False)


# class PlaylistSerializer(serializers.Serializer):
#     name = serializers.CharField()
#     description = serializers.CharField(required=False)
#     created_at = serializers.DateTimeField()
#     updated_at = serializers.DateTimeField()

