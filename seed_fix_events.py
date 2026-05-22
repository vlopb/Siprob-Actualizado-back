"""
Fix Events data: fill total_payable for qualifies=True events and create missing events.
"""
import os
import django
import random
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from records.models import Records, Events
from users.models import User

UMA_2024 = 108.57  # Valor UMA diario 2024 en MXN

CONDUCTA_ANTISOCIAL_FINES = {
    'Escandalo en via publica':       (2, 8),
    'Uso de lenguaje obsceno':         (2, 8),
    'Ingestion de alcohol en via publica': (3, 12),
    'Riña':                            (4, 24),
    'Grafiti':                         (4, 36),
    'Danos a propiedad':               (6, 48),
    'Desobediencia a autoridad':       (3, 24),
    'Ebriedad':                        (6, 24),
    'Disturbio en lugar publico':      (3, 12),
    'Violacion a reglamento':          (2, 8),
}

DEFAULT_FINE = (3, 16)

admin_user = User.objects.filter(discriminator='ADMIN').first() or User.objects.first()

# 1. Fix events with qualifies=True and total_payable=0
zero_events = Events.objects.filter(qualifies=True, total_payable=0)
print(f"Fixing {zero_events.count()} events with qualifies=True and total_payable=0...")

updated = 0
for event in zero_events:
    subtype = event.subtype or ''
    min_sal, qual_hrs = CONDUCTA_ANTISOCIAL_FINES.get(subtype, DEFAULT_FINE)
    # Add slight variation
    min_sal_actual = min_sal + random.choice([0, 0, 1, 2])
    qual_hrs_actual = qual_hrs + random.choice([0, 0, 4, 8, -4])
    qual_hrs_actual = max(4, qual_hrs_actual)
    total_payable = round(min_sal_actual * UMA_2024, 2)

    event.minimum_salaries = min_sal_actual
    event.qualified_hours = qual_hrs_actual
    event.total_payable = total_payable
    event.save()
    updated += 1

print(f"  Updated {updated} events with proper fines.")

# 2. Create events for records that have none
records_no_events = Records.objects.filter(
    has_been_released=False
).exclude(id__in=Events.objects.values_list('record_id', flat=True))

print(f"\nCreating events for {records_no_events.count()} records without events...")

INFRACTION_TYPES = [
    ('Conducta antisocial', 'Escandalo en via publica', True, 2, 8),
    ('Conducta antisocial', 'Ingestion de alcohol en via publica', True, 3, 12),
    ('Conducta antisocial', 'Uso de lenguaje obsceno', True, 2, 8),
    ('Conducta antisocial', 'Riña', True, 4, 24),
]

PLACES = [
    ('Av. Insurgentes y Reforma', 'Patrulla 12', 'Centro'),
    ('Calle Morelos #45', 'Patrulla 33', 'Norte'),
    ('Blvd. Hidalgo y Guerrero', 'Patrulla 8', 'Sur'),
]

for record in records_no_events:
    infraction = random.choice(INFRACTION_TYPES)
    place_data = random.choice(PLACES)
    min_sal_actual = infraction[3] + random.choice([0, 1])
    qual_hrs_actual = infraction[4]
    total_payable = round(min_sal_actual * UMA_2024, 2)

    event_dt = record.entry_date - timedelta(hours=random.randint(1, 3))
    detention_dt = record.entry_date - timedelta(minutes=random.randint(10, 60))

    Events.objects.create(
        record=record,
        qualifies=infraction[2],
        minimum_salaries=min_sal_actual,
        qualified_hours=qual_hrs_actual,
        total_payable=total_payable,
        basis='Reglamento de Policía y Buen Gobierno',
        event_datetime=event_dt,
        detention_datetime=detention_dt,
        detention_folio=f"DET-{record.folio_afi}",
        discriminator='Infracción',
        type=infraction[0],
        subtype=infraction[1],
        violence='Sin violencia',
        ambient='Via pública',
        movil='A pie',
        modus_operandi='Flagrante',
        event_description=f'El detenido fue encontrado en {place_data[0]} presentando conducta antisocial.',
        detention_type='Preventiva',
        reason='Alteración del orden público',
        arrested_by=admin_user,
        place=place_data[0],
        unit=place_data[1],
        sector=place_data[2],
        clasification='Infracción administrativa',
        locality='Centro Histórico',
        municipality='Municipio Central',
        country='México',
        street=place_data[0].split(' y ')[0] if ' y ' in place_data[0] else place_data[0],
        colony='Centro',
        created_by=admin_user,
        is_active=True,
    )
    print(f"  Created event for record {record.folio_afi}")

print("\nDone! Summary:")
print(f"  Events total: {Events.objects.count()}")
print(f"  Events with total_payable > 0: {Events.objects.filter(total_payable__gt=0).count()}")
print(f"  Active records without events: {Records.objects.filter(has_been_released=False).exclude(id__in=Events.objects.values_list('record_id', flat=True)).count()}")
