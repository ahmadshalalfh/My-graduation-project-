from django.db import models
from django.contrib.auth.models import AbstractUser

class myuser(AbstractUser):
   userID = models.IntegerField(primary_key=True)
   Address = models.CharField(max_length=255)
   Phone = models.CharField(max_length=20)
   is_employee = models.BooleanField(default=False)
   is_admin = models.BooleanField(default=False)



class users(models.Model):
    ID = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=255)

class Departments(models.Model):
    DepartmentID = models.AutoField(primary_key=True)
    DepartmentName = models.CharField(max_length=255)

class Employee(myuser):
   department = models.ForeignKey(Departments, on_delete=models.CASCADE)

class Announcements(models.Model):
    AnnouncementsID = models.AutoField(primary_key=True)
    Title = models.CharField(max_length=255)
    Content = models.TextField()
    Date = models.DateTimeField()
    Announcementsimage = models.BinaryField(null=True)

class News(models.Model):
    NewsID = models.AutoField(primary_key=True)
    Title = models.CharField(max_length=255)
    Content = models.TextField()
    Date = models.DateTimeField()
    Newsimage = models.BinaryField(null=True)

class Messages(models.Model):
    MessageID = models.AutoField(primary_key=True)
    Content = models.TextField()
    SendDate = models.DateTimeField()
    ReadStatus = models.BooleanField(default=False)
    sender = models.ForeignKey(myuser,related_name='received_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(myuser,related_name='sender_messages', on_delete=models.CASCADE)
    

class Requests(models.Model):
    RequestID = models.AutoField(primary_key=True)
    CitizenID = models.ForeignKey(myuser, on_delete=models.CASCADE)
    DepartmentID = models.ForeignKey(Departments, on_delete=models.CASCADE)
    RequestDate = models.DateTimeField()
    Details = models.TextField()
    ID_Photo = models.BinaryField(null = True)
    Status = models.TextField(null = True)
    Type = models.TextField(null = True)

class Bills(models.Model):
    BillID = models.AutoField(primary_key=True)
    RequestID = models.ForeignKey(Requests, on_delete=models.CASCADE)
    CitizenID = models.ForeignKey(myuser, on_delete=models.CASCADE)
    Amount = models.FloatField()
    DueDate = models.DateTimeField()
    paid = models.BooleanField()

class Payments(models.Model):
    PaymentID = models.AutoField(primary_key=True)
    BillID = models.ForeignKey(Bills, on_delete=models.CASCADE)
    AmountPaid = models.FloatField()
    PaymentDate = models.DateTimeField()

class WaterDepartmentRequests(Requests):
    BuildingPermit_Photo = models.BinaryField(null = True)
    Oldsubscription_Photo = models.BinaryField(null = True)
   

class ElectricityDepartmentRequests(Requests):
    BuildingPermit_Photo = models.BinaryField(null = True)
    Oldsubscription_Photo = models.BinaryField(null = True)

class AdministrationDermentRequests(Requests):
    Bill_Photo = models.BinaryField()
    Rent_Photo = models.BinaryField()
    

class ComplaintsDepartmentRequests(Requests):
    Supportive_Photo = models.BinaryField()
    

class EngineeringDepartmentRequests(Requests):
    SpacePlan_Photo = models.BinaryField(null = True)
    CertifiedEngineeringPlan_Photo = models.BinaryField(null = True)
    Ownership_Photo = models.BinaryField(null = True)
    Geometricscheme_Photo = models.BinaryField(null = True)
    CourtAffidavit_Photo = models.BinaryField(null = True)
     

class Subscriptions(models.Model):
    SubscriptionID = models.AutoField(primary_key=True)
    Name = models.TextField(null = True)
    CitizenID = models.ForeignKey(myuser, on_delete=models.CASCADE)
    DepartmentID = models.ForeignKey(Departments, on_delete=models.CASCADE)
    Subscription_photo = models.BinaryField(null = True)

class Notices(models.Model):
    NoticesID = models.AutoField(primary_key=True)
    CitizenID = models.ForeignKey(myuser, on_delete=models.CASCADE)
    Details = models.TextField()
    DueDate = models.DateTimeField(null = True)
    ReadStatus = models.BooleanField(default=False)