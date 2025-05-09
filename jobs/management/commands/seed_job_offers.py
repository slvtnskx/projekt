import json
from django.core.management.base import BaseCommand
from jobs.models import JobOffer
from django.utils.dateparse import parse_datetime

class Command(BaseCommand):
    help = 'Seed the database with job offers from job_offers.jsonl.'

    def handle(self, *args, **kwargs):
        path = 'jobs/data/job_offers.jsonl'
        JobOffer.objects.all().delete()
        with open(path, encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                JobOffer.objects.create(
                    offer_id=data.get('id'),
                    last_modified=parse_datetime(data.get('lastModified')) if data.get('lastModified') else None,
                    min_wage_hourly=data.get('minWageHourly'),
                    min_wage_monthly=data.get('minWageMonthly'),
                    region=data.get('region'),
                    district=data.get('district'),
                    municipality=data.get('municipality'),
                    city_part=data.get('cityPart'),
                    profession=data.get('profession'),
                    text_to_search=data.get('textToSearch'),
                    education=data.get('education'),
                    shifts=data.get('shifts'),
                    hours=data.get('hours'),
                    full_time=data.get('fullTime', False),
                    part_time=data.get('partTime', False),
                    freelance_work=data.get('freelanceWork', False),
                    short_term_employment=data.get('shortTermEmployment', False),
                    civil_service=data.get('civilService', False),
                    agency_contract=data.get('agencyContract', False),
                    agency_temporary_staffing=data.get('agencyTemporaryStaffing', False),
                    asylum_seeker=data.get('asylumSeeker', False),
                    non_eu_national=data.get('nonEUnational', False),
                    blue_card=data.get('blueCard', False),
                    employee_card=data.get('employeeCard', False),
                    display_information=data.get('displayInformation'),
                    # Fallbacks for required fields
                    title=data.get('profession', 'Unknown'),
                    description=data.get('textToSearch', ''),
                    company='',
                    location=data.get('region') or data.get('district') or data.get('municipality') or '',
                )
        self.stdout.write(self.style.SUCCESS('Database seeded from job_offers.jsonl.'))
