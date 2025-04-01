from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import LineUser, LineMessage, LineMessageAttachment

User = get_user_model()

class UserSimpleSerializer(serializers.ModelSerializer):
    """簡化的用戶序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'phone', 'email', 'is_line_bound']

class LineMessageAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineMessageAttachment
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class LineMessageSerializer(serializers.ModelSerializer):
    attachments = LineMessageAttachmentSerializer(many=True, read_only=True)
    line_user_name = serializers.CharField(source='line_user.display_name', read_only=True)
    user_name = serializers.CharField(source='line_user.user.username', read_only=True)
    
    class Meta:
        model = LineMessage
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'delivery_time', 'error_message')
    
    def validate_message(self, value):
        """驗證消息內容"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("消息內容不能為空")
        if len(value) > 2000:  # LINE 消息長度限制
            raise serializers.ValidationError("消息長度不能超過2000字符")
        return value.strip()

class LineUserSerializer(serializers.ModelSerializer):
    """LINE用戶序列化器"""
    user = UserSimpleSerializer(read_only=True)
    messages = LineMessageSerializer(many=True, read_only=True, source='linemessage_set')
    message_count = serializers.IntegerField(read_only=True)
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = LineUser
        fields = [
            'id', 'user', 'line_user_id', 'display_name', 'status_message',
            'picture_url', 'language', 'last_interaction', 'messages',
            'message_count', 'last_message'
        ]
        read_only_fields = ('created_at', 'updated_at', 'last_interaction')
    
    def get_last_message(self, obj):
        """獲取最後一條消息"""
        last_message = obj.linemessage_set.order_by('-send_time').first()
        if last_message:
            return {
                'content': last_message.message,
                'type': last_message.message_type,
                'time': last_message.send_time,
                'is_sent': last_message.is_sent
            }
        return None
    
    def to_representation(self, instance):
        """增加額外的統計信息"""
        data = super().to_representation(instance)
        data['message_count'] = instance.linemessage_set.count()
        data['unread_count'] = instance.linemessage_set.filter(
            is_sent=False, 
            status='delivered'
        ).count()
        return data

class LineUserBindSerializer(serializers.Serializer):
    """LINE用戶綁定序列化器"""
    user_id = serializers.IntegerField(required=True)
    
    def validate_user_id(self, value):
        try:
            user = User.objects.get(id=value)
            if user.is_line_bound:
                raise serializers.ValidationError("該用戶已綁定其他LINE帳號")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("用戶不存在")
    
    def create(self, validated_data):
        user = User.objects.get(id=validated_data['user_id'])
        line_user = self.context['line_user']
        line_user.bind_user(user)
        return line_user

class LineUserUnbindSerializer(serializers.Serializer):
    """LINE用戶解綁序列化器"""
    confirm = serializers.BooleanField(required=True)
    
    def validate_confirm(self, value):
        if not value:
            raise serializers.ValidationError("請確認解綁操作")
        return value
    
    def create(self, validated_data):
        line_user = self.context['line_user']
        line_user.unbind_user()
        return line_user