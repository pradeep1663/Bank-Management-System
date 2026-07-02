from django.db import models

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=100)
    user_password = models.CharField(max_length=255)
    user_role = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'users'

class Account(models.Model):
    account_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    account_type = models.CharField(max_length=20)
    account_balance = models.DecimalField(max_digits=15, decimal_places=2)
    
    class Meta:
        db_table = 'accounts'

class Request(models.Model):
    req_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    req_type = models.CharField(max_length=20)
    req_amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20, default='Pending')
    
    class Meta:
        db_table = 'requests'
class Response(models.Model):
    response_id = models.AutoField(primary_key=True)
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    response_text = models.TextField()
    response_date = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'response'