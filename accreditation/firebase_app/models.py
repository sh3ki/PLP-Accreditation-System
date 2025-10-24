from django.db import models

# Create your models here.

class Program(models.Model):
    """
    Program model stored in Firebase
    Represents academic programs within departments
    """
    code = models.CharField(max_length=20, unique=True, primary_key=True)
    name = models.CharField(max_length=200)
    department_id = models.CharField(max_length=20)  # Foreign key to department code
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'programs'
        managed = False  # Firebase manages this collection
        
    def __str__(self):
        return f"{self.code} - {self.name}"


class AccreditationType(models.Model):
    """
    Accreditation Type model stored in Firebase
    Represents accreditation types within programs
    """
    id = models.CharField(max_length=50, unique=True, primary_key=True)
    name = models.CharField(max_length=200)
    program_id = models.CharField(max_length=20)  # Foreign key to program code
    logo_url = models.URLField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'accreditation_types'
        managed = False  # Firebase manages this collection
        
    def __str__(self):
        return f"{self.name}"


class Area(models.Model):
    """
    Area model stored in Firebase
    Represents areas within accreditation types
    """
    id = models.CharField(max_length=50, unique=True, primary_key=True)
    name = models.CharField(max_length=200)
    accreditation_type_id = models.CharField(max_length=50)  # Foreign key to accreditation type
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'areas'
        managed = False  # Firebase manages this collection
        
    def __str__(self):
        return f"{self.name}"


class Checklist(models.Model):
    """
    Checklist model stored in Firebase
    Represents checklists within areas
    """
    id = models.CharField(max_length=50, unique=True, primary_key=True)
    name = models.CharField(max_length=200)
    area_id = models.CharField(max_length=50)  # Foreign key to area
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'checklists'
        managed = False  # Firebase manages this collection
        
    def __str__(self):
        return f"{self.name}"
