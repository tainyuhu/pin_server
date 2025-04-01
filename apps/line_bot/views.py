from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model

import json
import secrets
import logging
import requests

from .models import LineUser
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)

logger = logging.getLogger(__name__)
User = get_user_model()

# LINE Bot 設定
configuration = Configuration(access_token=settings.LINE_BOT_CONFIG['ACCESS_TOKEN'])
handler = WebhookHandler(settings.LINE_BOT_CONFIG['CHANNEL_SECRET'])

@csrf_exempt
@require_http_methods(["POST"])
def webhook(request):
    """LINE Webhook 處理"""
    signature = request.headers.get('x-line-signature', '')
    body = request.body.decode('utf-8')
    
    try:
        if not body:
            logger.warning("Empty request body")
            return HttpResponse(status=200)
        
        handler.handle(body, signature)
        payload = json.loads(body)
        events = payload.get('events', [])
        
        for event in events:
            handle_message(event)
            
    except InvalidSignatureError:
        logger.error("Invalid signature")
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
    
    return HttpResponse(status=200)

def handle_message(event):
    """處理 LINE 訊息"""
    try:
        user_id = event['source']['userId']
        message = event['message']
        reply_token = event['replyToken']
        
        # 取得或創建 LINE 用戶資料
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            profile = line_bot_api.get_profile(user_id)
            
        line_user, created = LineUser.objects.get_or_create(
            line_user_id=user_id,
            defaults={
                'display_name': profile.display_name,
                'picture_url': profile.picture_url or '',
                'status_message': profile.status_message or ''
            }
        )
        
        # 發送回覆
        send_reply(reply_token, "已收到您的訊息")
        
    except Exception as e:
        logger.error(f"Error in handle_message: {str(e)}")

def send_reply(reply_token, text):
    """發送回覆訊息"""
    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            message_request = ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=text)]
            )
            line_bot_api.reply_message(message_request)
    except Exception as e:
        logger.error(f"Error sending reply: {str(e)}")

@api_view(['GET'])
def check_bind_status(request, id):
    """檢查使用者是否已綁定LINE"""
    user = get_object_or_404(User, id=id)
    return Response({
        'is_bound': user.is_line_bound,
        'bind_time': user.line_bind_time
    })

@api_view(['GET'])
def get_line_login_url(request):
    """獲取 LINE Login URL"""
    try:
        state = secrets.token_urlsafe(32)  # 生成隨機 state
        user_id = request.GET.get('user_id')
        
        if not user_id:
            return Response({'error': '未提供使用者ID'}, status=400)
            
        # 將 user_id 存入 cache
        cache.set(f"line_state_{state}", user_id, 300)  # 5分鐘過期
        
        login_url = (
            f"https://access.line.me/oauth2/v2.1/authorize"
            f"?response_type=code"
            f"&client_id={settings.LINE_LOGIN_CONFIG['CHANNEL_ID']}"
            f"&redirect_uri={settings.LINE_LOGIN_CONFIG['CALLBACK_URL']}"
            f"&state={state}"
            f"&scope=profile"
        )
        
        return Response({
            'login_url': login_url,
            'state': state
        })
        
    except Exception as e:
        logger.error(f"Error generating LINE login URL: {str(e)}")
        return Response({'error': '生成登入連結失敗'}, status=500)

@api_view(['POST']) 
def handle_line_login(request):
    """處理 LINE Login 回調"""
    try:
        code = request.data.get('code')
        state = request.data.get('state')
        
        # 驗證 state
        user_id = cache.get(f"line_state_{state}")
        if not user_id:
            return Response({'error': '無效的授權請求'}, status=400)
        
        # 取得 access token
        token_response = requests.post(
            'https://api.line.me/oauth2/v2.1/token',
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': settings.LINE_LOGIN_CONFIG['CALLBACK_URL'],
                'client_id': settings.LINE_LOGIN_CONFIG['CHANNEL_ID'],
                'client_secret': settings.LINE_LOGIN_CONFIG['CHANNEL_SECRET']
            }
        )
        
        if token_response.status_code != 200:
            raise Exception('獲取 LINE token 失敗')
            
        token_data = token_response.json()
        
        # 取得用戶資料
        profile_response = requests.get(
            'https://api.line.me/v2/profile',
            headers={'Authorization': f"Bearer {token_data['access_token']}"}
        )
        
        if profile_response.status_code != 200:
            raise Exception('獲取 LINE 用戶資料失敗')
            
        profile_data = profile_response.json()
        
        # 取得或創建 LINE 用戶
        line_user, created = LineUser.objects.get_or_create(
            line_user_id=profile_data['userId'],
            defaults={
                'display_name': profile_data['displayName'],
                'picture_url': profile_data.get('pictureUrl', ''),
                'status_message': profile_data.get('statusMessage', '')
            }
        )
        
        # 綁定用戶
        user = User.objects.get(id=user_id)
        line_user.user = user
        line_user.save()
        
        # 清除 state 快取
        cache.delete(f"line_state_{state}")
        
        return Response({
            'message': 'LINE 綁定成功',
            'line_user_id': line_user.line_user_id,
            'display_name': line_user.display_name
        })
        
    except Exception as e:
        logger.error(f"Error handling LINE login: {str(e)}")
        return Response({'error': str(e)}, status=500)

