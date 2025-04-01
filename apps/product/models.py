from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords
from apps.system.models import User
from utils.model import SoftModel, BaseModel

class ProductCategory(BaseModel):
    """產品類別"""
    name = models.CharField("類別名稱", max_length=50)
    code = models.CharField("類別代碼", max_length=50, unique=True)
    description = models.TextField("類別描述", blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_product_categories", verbose_name="建立者"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="updated_product_categories", verbose_name="更新者"
    )
    history = HistoricalRecords()  # 追蹤歷史變更
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "產品類別"
        verbose_name_plural = "產品類別"
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['name'])
        ]


class Product(SoftModel):
    """產品品號 (使用軟刪除)"""
    product_code = models.CharField("品號", max_length=50, unique=True)
    product_name = models.CharField("品名", max_length=100)
    category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE, related_name="products", verbose_name="類別"
    )
    specification = models.CharField("規格", max_length=200)
    unit = models.CharField("單位", max_length=20)
    box_size = models.PositiveIntegerField("裝箱容量", null=True, blank=True)
    status = models.BooleanField("狀態", default=True)
    remark = models.TextField("備註", blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_products", verbose_name="建立者"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="updated_products", verbose_name="更新者"
    )
    history = HistoricalRecords()  # 追蹤歷史變更
    
    def __str__(self):
        return f"{self.product_code} - {self.product_name}"
    
    class Meta:
        verbose_name = "產品品號"
        verbose_name_plural = "產品品號"
        ordering = ['product_code']
        indexes = [
            models.Index(fields=['product_code']),
            models.Index(fields=['category'])
        ]


class ProductHistory(SoftModel):
    """產品品號異動歷史 (使用軟刪除)"""
    TYPE_CHOICES = (
        ('create', '新增'),
        ('update', '修改'),
        ('delete', '刪除'),
    )
    
    datetime = models.DateTimeField("異動時間", auto_now_add=True)
    type = models.CharField("異動類型", max_length=10, choices=TYPE_CHOICES)
    product_code = models.CharField("品號", max_length=50, db_index=True)
    field = models.CharField("異動欄位", max_length=50)
    before_value = models.TextField("變更前值", blank=True)
    after_value = models.TextField("變更後值", blank=True)
    operator = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="product_histories", verbose_name="操作人員"
    )
    remark = models.TextField("備註", blank=True, null=True)
    
    def __str__(self):
        return f"{self.product_code} - {self.type} - {self.datetime}"
    
    class Meta:
        verbose_name = "品號異動歷史"
        verbose_name_plural = "品號異動歷史"
        ordering = ['-datetime']
        indexes = [
            models.Index(fields=['-datetime']),
            models.Index(fields=['product_code', '-datetime'])
        ]