from django.core.management.base import BaseCommand
from jobs.models import JobOffer
from datetime import date, timedelta
import random
import json

with open('jobs/data/locations.json') as f:
    locations = json.load(f)

class Command(BaseCommand):
    help = 'Seed the database with sample job offers.'

    def handle(self, *args, **kwargs):
        JobOffer.objects.all().delete()
        titles = [
            'Software Engineer', 'Data Analyst', 'Frontend Developer', 'Backend Developer',
            'Project Manager', 'QA Engineer', 'DevOps Engineer', 'Product Owner',
            'UI/UX Designer', 'Mobile Developer', 'Cloud Architect', 'Support Engineer',
            'Business Analyst', 'AI Engineer', 'ML Engineer', 'Full Stack Developer',
            'Database Administrator', 'Network Engineer', 'Security Specialist', 'Scrum Master'
        ]
        companies = [
            'Tech Solutions', 'Data Insights', 'Creative Web', 'Business Corp',
            'NextGen Apps', 'Cloudify', 'SecureIT', 'WebWorks', 'Appify', 'InnovateX'
        ]
        locations = [
            'New York', 'San Francisco', 'Remote', 'Chicago', 'Austin',
            'Seattle', 'Boston', 'Los Angeles', 'Denver', 'Atlanta'
        ]
        descriptions = [
            'Work on exciting projects with a dynamic team.',
            'Develop and maintain scalable applications.',
            'Collaborate with cross-functional teams.',
            'Drive innovation and deliver high-quality solutions.',
            'Analyze requirements and implement features.'
        ]
        today = date.today()
        for i in range(100):
            JobOffer.objects.create(
                title=random.choice(titles),
                description=random.choice(descriptions),
                company=random.choice(companies),
                location=random.choice(locations),
                date_posted=today - timedelta(days=random.randint(0, 30))
            )
        self.stdout.write(self.style.SUCCESS('Database seeded with 100 sample job offers.'))