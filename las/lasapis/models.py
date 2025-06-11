from django.contrib.gis.db import models  # Use GIS model for geometry field
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.db.models.functions import Transform

class Project(models.Model):
    id = models.BigIntegerField(unique=True)  # Explicit if needed
    uid = models.CharField(max_length=255, primary_key=True)  # Primary key
    name = models.CharField(max_length=255)
    name_m = models.CharField(max_length=255)
    remark = models.CharField(max_length=255)
    geom = models.GeometryField()

    class Meta:
        db_table = 'project'
        managed = False  # Set to False if Django shouldn't manage the table



class Centreline(models.Model):
    id = models.BigIntegerField(unique=True)  # Explicit if needed
    uid = models.CharField(max_length=255, primary_key=True)  # Primary key
    fid = models.ForeignKey(
        Project,
        to_field='uid',  # ForeignKey to Project.uid
        db_column='fid',  # Column name in the database
        on_delete=models.DO_NOTHING
    )
    geom = models.GeometryField()

    class Meta:
        db_table = 'centerline'
        managed = False  # Set to False if Django shouldn't manage the table




class District(models.Model):
    id = models.BigIntegerField(unique=True)
    uid = models.CharField(max_length=255, primary_key=True)
    fid = models.ForeignKey(
        Project,
        to_field='uid',         # ForeignKey to Project.uid
        db_column='fid',        # Column name in the database
        on_delete=models.DO_NOTHING
    )
    name = models.CharField(max_length=255)
    name_m = models.CharField(max_length=255)
    geom = models.GeometryField()

    class Meta:
        db_table = 'district'
        managed = False


class Taluka(models.Model):
    id = models.BigIntegerField(unique=True)
    uid = models.CharField(max_length=255, primary_key=True)
    fid = models.ForeignKey(
        District,
        to_field='uid',         # ForeignKey to Project.uid
        db_column='fid',        # Column name in the database
        on_delete=models.DO_NOTHING
    )
    name = models.CharField(max_length=255)
    name_m = models.CharField(max_length=255)
    geom = models.GeometryField()

    class Meta:
        db_table = 'taluka'
        managed = False


class Village(models.Model):
    id = models.BigIntegerField(unique=True)
    uid = models.CharField(max_length=255, primary_key=True)
    fid = models.ForeignKey(
        Taluka,
        to_field='uid',         # ForeignKey to Project.uid
        db_column='fid',        # Column name in the database
        on_delete=models.DO_NOTHING
    )
    name = models.CharField(max_length=255)
    name_m = models.CharField(max_length=255)
    geom = models.GeometryField()

    class Meta:
        db_table = 'village'
        managed = False

class Gut(models.Model):
    id = models.BigIntegerField(unique=True)
    uid = models.CharField(max_length=255, primary_key=True)
    fid = models.ForeignKey(
        Village,
        to_field='uid',         # ForeignKey to Project.uid
        db_column='fid',        # Column name in the database
        on_delete=models.DO_NOTHING
    )
    name = models.CharField(max_length=255)
    name_m = models.CharField(max_length=255)
    geom = models.GeometryField()

    class Meta:
        #   class Meta:
        indexes = [
            models.Index(fields=['fid']),
            models.Index(fields=['name_m']),
        ]
        db_table = 'gut'
        managed = False


class Bund(models.Model):
    id = models.BigIntegerField(unique=True)
    uid = models.CharField(max_length=255, primary_key=True)
    fid = models.ForeignKey(
        Gut,
        to_field='uid',         # ForeignKey to Project.uid
        db_column='fid',        # Column name in the database
        on_delete=models.DO_NOTHING
    )
    name = models.CharField(max_length=255)
    name_m = models.CharField(max_length=255)
    geom = models.GeometryField()
    acquiretype  = models.CharField(max_length=255)
    ownertype = models.CharField(max_length=255)
    permtype = models.CharField(max_length=255)
    taxlandtype = models.CharField(max_length=255)
    sdolandtype = models.CharField(max_length=255)
    totaltax = models.DecimalField(max_digits=10, decimal_places=2)
    totalgutarea = models.DecimalField(max_digits=10, decimal_places=2)
    valdecided = models.DecimalField(max_digits=10, decimal_places=2)
    valdeduction = models.DecimalField(max_digits=10, decimal_places=2)


    class Meta:
        db_table = 'bund'
        managed = False