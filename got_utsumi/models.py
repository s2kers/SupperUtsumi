from django.db import models


class Employee(models.Model):
    empid = models.CharField(max_length=8, primary_key=True)
    empfname = models.CharField(max_length=64)
    emplname = models.CharField(max_length=64)
    emppasswd = models.CharField(max_length=256)
    emprole = models.IntegerField()

    def __str__(self):
        return f'{self.empfname} {self.emplname}'


class Shiiregyosha(models.Model):
    shiireid = models.CharField(max_length=8, primary_key=True)
    shiiremei = models.CharField(max_length=64)
    shiireaddress = models.CharField(max_length=64)
    shiiretel = models.CharField(max_length=13)
    shihonkin = models.IntegerField()
    nouki = models.IntegerField()


class Patient(models.Model):
    patid = models.CharField(max_length=8, primary_key=True)
    patfname = models.CharField(max_length=64)
    patlname = models.CharField(max_length=64)
    hokenmei = models.CharField(max_length=64)
    hokenexp = models.DateField()


class Medicine(models.Model):
    medicineid = models.CharField(max_length=8, primary_key=True)
    medicinename = models.CharField(max_length=64)
    unit = models.CharField(max_length=8)


class Treatment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
