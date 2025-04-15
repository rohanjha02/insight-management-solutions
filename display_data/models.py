from django.db import models

class Complaint(models.Model):
    branch = models.CharField(max_length=255)
    branch_code = models.CharField(max_length=20)
    branch_name = models.CharField(max_length=255)
    complaint_description = models.TextField()
    email = models.EmailField()
    machine_serial_number = models.CharField(max_length=255)
    machine_type = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=20)
    state = models.CharField(max_length=50)
    assigned_engineer = models.CharField(max_length=255)
    remarks = models.TextField(blank=True)  # Optional field for remarks

    def __str__(self):
        return f"Complaint ID: {self.id} - Branch: {self.branch}"