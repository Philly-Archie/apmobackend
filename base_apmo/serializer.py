from rest_framework import serializers
from .models import Sermon, Devotion, Events, Category

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


class DevotionSerializer(serializers.ModelSerializer):
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