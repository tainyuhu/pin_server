from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 創建路由器
router = DefaultRouter()
# router.register(r'line-users', views.LineUserViewSet)
# router.register(r'line-messages', views.LineMessageViewSet)

# URL patterns
urlpatterns = [
    # Webhook
    path('webhook/', views.webhook, name='webhook'),
    
    # LINE Login
    path('login/url/', views.get_line_login_url, name='login_url'),
    path('login/callback/', views.handle_line_login, name='login_callback'),
    
    # 綁定狀態
    path('bind/status/<int:id>/', views.check_bind_status, name='bind_status'),
]

# API 端點列表（供參考）:
"""
LINE User endpoints:
- GET    /api/line-users/                - 獲取所有LINE用戶列表
- POST   /api/line-users/                - 創建LINE用戶
- GET    /api/line-users/{id}/           - 獲取特定LINE用戶詳情
- PUT    /api/line-users/{id}/           - 更新特定LINE用戶
- DELETE /api/line-users/{id}/           - 刪除特定LINE用戶
- POST   /api/line-users/{id}/bind_user/ - 綁定系統用戶
- POST   /api/line-users/{id}/unbind_user/ - 解除綁定
- POST   /api/line-users/{id}/send_message/ - 發送消息
- GET    /api/line-users/{id}/message_statistics/ - 獲取消息統計
- GET    /api/line-users/binding_statistics/ - 獲取綁定統計

LINE Message endpoints:
- GET    /api/line-messages/             - 獲取所有消息列表
- POST   /api/line-messages/             - 創建新消息
- GET    /api/line-messages/{id}/        - 獲取特定消息詳情
- PUT    /api/line-messages/{id}/        - 更新特定消息
- DELETE /api/line-messages/{id}/        - 刪除特定消息
- POST   /api/line-messages/bulk_send/   - 批量發送消息

統計相關:
- GET    /api/statistics/daily-activity/ - 獲取每日活動統計

LINE Login:
- GET    /api/line-login-url/           - 獲取LINE登入URL
- POST   /api/line-login-callback/      - 處理LINE登入回調

Webhook:
- POST   /webhook/                      - LINE Webhook接收端點
"""