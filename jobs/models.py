from django.db import models

class JobOffer(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    company = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    date_posted = models.DateField(auto_now_add=True)

    offer_id = models.BigIntegerField(unique=True, null=True, blank=True)
    last_modified = models.DateTimeField(null=True, blank=True)
    min_wage_hourly = models.FloatField(null=True, blank=True)
    min_wage_monthly = models.FloatField(null=True, blank=True)
    region = models.CharField(max_length=32, null=True, blank=True)
    district = models.CharField(max_length=32, null=True, blank=True)
    municipality = models.CharField(max_length=32, null=True, blank=True)
    city_part = models.CharField(max_length=64, null=True, blank=True)
    profession = models.CharField(max_length=32, null=True, blank=True)
    text_to_search = models.TextField(null=True, blank=True)
    education = models.CharField(max_length=64, null=True, blank=True)
    shifts = models.CharField(max_length=32, null=True, blank=True)
    hours = models.FloatField(null=True, blank=True)
    full_time = models.BooleanField(default=False)
    part_time = models.BooleanField(default=False)
    freelance_work = models.BooleanField(default=False)
    short_term_employment = models.BooleanField(default=False)
    civil_service = models.BooleanField(default=False)
    agency_contract = models.BooleanField(default=False)
    agency_temporary_staffing = models.BooleanField(default=False)
    asylum_seeker = models.BooleanField(default=False)
    non_eu_national = models.BooleanField(default=False)
    blue_card = models.BooleanField(default=False)
    employee_card = models.BooleanField(default=False)
    display_information = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.profession} (ID: {self.offer_id})"
