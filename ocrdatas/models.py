from django.db import models

# Create your models here.


class OcrDatas(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    test1 = models.CharField(max_length=10)
    test2 = models.CharField(max_length=10)
    test3 = models.CharField(max_length=10)
    test4 = models.CharField(max_length=10)


    class Meta:
        ordering = ['created']



