import os, sys
sys.path.insert(0, '/usr/src/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()
"""
Script de datos de prueba para SIPROB.
Ejecutar con: docker exec -i siprob-api python manage.py shell < /tmp/seed_dummy.py
"""
from django.utils import timezone
from datetime import timedelta
from districts.models import District
from users.models import User
from detainees.models import Detainee, Photos, Addresses, Phones, FakeNames
from records.models import (
    Records, Cells, Events, MedicalInformation,
    Belongings, Actions, Faults, RecordsPoliceAgents
)

print("Cargando distritos...")
norte   = District.objects.get(name='Norte')
sur     = District.objects.get(name='Sur')
oriente = District.objects.get(name='Oriente')
poniente= District.objects.get(name='Poniente')

print("Configurando usuarios...")
usuario = User.objects.get(username='Usuario')
usuario.district_default = norte
usuario.name = 'Administrador'
usuario.fathers_name = 'Sistema'
usuario.mothers_name = 'SIPROB'
usuario.employee_number = 'ADM-001'
usuario.save()

karsam = User.objects.get(username='karsam')
karsam.district_default = sur
karsam.name = 'Carlos'
karsam.fathers_name = 'Ramírez'
karsam.mothers_name = 'Sánchez'
karsam.employee_number = 'MED-002'
karsam.detainee_module = True
karsam.detainee_show   = True
karsam.records_module  = True
karsam.medic_show      = True
karsam.medic_create    = True
karsam.medic_edit      = True
karsam.save()
print("  ✓ Usuarios actualizados")

# ── DETENIDOS ──────────────────────────────────────────────────────────────────
print("Creando detenidos...")

detenidos_data = [
    dict(name='Juan Carlos',  fathers_name='Martínez',  mothers_name='López',
         birth_date='1990-03-15', age=34, gender='Masculino',
         marital_status='Soltero', nationality='Mexicana',
         occupation='Empleado', schooling='Preparatoria',
         notes='Reincidente conocido'),
    dict(name='María Elena',  fathers_name='García',    mothers_name='Hernández',
         birth_date='1985-07-22', age=39, gender='Femenino',
         marital_status='Casada', nationality='Mexicana',
         occupation='Ama de casa', schooling='Secundaria',
         notes=None),
    dict(name='Roberto',      fathers_name='Sánchez',   mothers_name='Flores',
         birth_date='1998-11-08', age=26, gender='Masculino',
         marital_status='Soltero', nationality='Mexicana',
         occupation='Desempleado', schooling='Primaria',
         notes='Sin identificación'),
    dict(name='Ana Sofía',    fathers_name='Torres',    mothers_name='Vega',
         birth_date='2000-01-30', age=24, gender='Femenino',
         marital_status='Soltera', nationality='Mexicana',
         occupation='Estudiante', schooling='Universidad',
         notes=None),
    dict(name='Miguel Ángel', fathers_name='Reyes',     mothers_name='Cruz',
         birth_date='1975-09-12', age=49, gender='Masculino',
         marital_status='Divorciado', nationality='Mexicana',
         occupation='Comerciante', schooling='Preparatoria',
         notes='Conocido por autoridades'),
    dict(name='Lucía',        fathers_name='Moreno',    mothers_name='Ramírez',
         birth_date='1992-05-18', age=32, gender='Femenino',
         marital_status='Unión libre', nationality='Mexicana',
         occupation='Vendedora', schooling='Secundaria',
         notes=None),
]

detenidos = []
for d in detenidos_data:
    det, created = Detainee.objects.get_or_create(
        name=d['name'], fathers_name=d['fathers_name'],
        defaults=d
    )
    detenidos.append(det)
    if created:
        print(f"  ✓ {det.name} {det.fathers_name}")
    else:
        print(f"  ~ {det.name} {det.fathers_name} (ya existía)")

# Teléfonos
from detainees.models import Phones
phones_data = [
    (detenidos[0], '6561234567', 'Personal'),
    (detenidos[1], '6569876543', 'Casa'),
    (detenidos[2], '6561112233', 'Personal'),
    (detenidos[4], '6564455667', 'Trabajo'),
]
for det, num, desc in phones_data:
    Phones.objects.get_or_create(detainee=det, phone_number=num, defaults={'description': desc})

# Direcciones
Addresses.objects.get_or_create(
    detainee=detenidos[0], discriminator='domicilio',
    defaults=dict(street='Av. Juárez', exterior_number='123', colony='Centro',
                  municipality='Juárez', state='Chihuahua', country='México')
)
Addresses.objects.get_or_create(
    detainee=detenidos[1], discriminator='domicilio',
    defaults=dict(street='Calle Reforma', exterior_number='456', colony='División del Norte',
                  municipality='Juárez', state='Chihuahua', country='México')
)
print("  ✓ Teléfonos y direcciones creados")

# ── EXPEDIENTES (RECORDS) ──────────────────────────────────────────────────────
print("Creando expedientes...")

now = timezone.now()

expedientes = [
    dict(detainee=detenidos[0], district=norte,   entry_date=now - timedelta(days=2),
         folio_afi='AFI-2026-001', process='Falta administrativa',
         fundament=24, sanction='Arresto 36 horas', has_been_released=False),
    dict(detainee=detenidos[1], district=sur,     entry_date=now - timedelta(days=1),
         folio_afi='AFI-2026-002', process='Falta administrativa',
         fundament=12, sanction='Multa', has_been_released=False),
    dict(detainee=detenidos[2], district=oriente, entry_date=now - timedelta(hours=8),
         folio_afi='AFI-2026-003', process='Delito',
         fundament=0, sanction='Puesta a disposición', has_been_released=False),
    dict(detainee=detenidos[3], district=poniente, entry_date=now - timedelta(days=3),
         folio_afi='AFI-2026-004', process='Falta administrativa',
         fundament=6, sanction='Amonestación',
         has_been_released=True,
         official_release_date=now - timedelta(days=2)),
    dict(detainee=detenidos[4], district=norte,   entry_date=now - timedelta(days=5),
         folio_afi='AFI-2026-005', process='Delito',
         fundament=0, sanction='Puesta a disposición',
         has_been_released=True,
         official_release_date=now - timedelta(days=4)),
    dict(detainee=detenidos[5], district=sur,     entry_date=now - timedelta(hours=3),
         folio_afi='AFI-2026-006', process='Falta administrativa',
         fundament=8, sanction='Arresto 24 horas', has_been_released=False),
]

records = []
for e in expedientes:
    rec, created = Records.objects.get_or_create(
        folio_afi=e['folio_afi'], defaults=e
    )
    records.append(rec)
    status = '✓' if created else '~'
    print(f"  {status} Expediente {rec.folio_afi}")

# ── CELDAS ─────────────────────────────────────────────────────────────────────
print("Creando asignaciones de celda...")
celdas_data = [
    (records[0], 'A-01', 'Sin novedades', 'JVALENZUELA'),
    (records[1], 'B-03', 'Detenida colaborativa', 'PMENDOZA'),
    (records[2], 'C-02', 'Vigilancia especial', 'RGARCIA'),
    (records[5], 'A-04', None, 'JVALENZUELA'),
]
celdas = []
for rec, cell, notes, registered_by in celdas_data:
    c, created = Cells.objects.get_or_create(
        record=rec, cell=cell,
        defaults=dict(cell_notes=notes, registered_by=registered_by,
                      registered_belongings=True, total_belongings=3,
                      registered_calls=False, total_calls=0)
    )
    celdas.append(c)
    if created:
        print(f"  ✓ Celda {cell} → {rec.folio_afi}")

# ── PERTENENCIAS ───────────────────────────────────────────────────────────────
if celdas:
    Belongings.objects.get_or_create(
        cell=celdas[0],
        defaults=dict(
            registration_datetime=now - timedelta(days=2),
            document_ine=True,
            devices_cellphone=True, devices_notes='iPhone negro',
            money_mexican_pesos=350, money_american_dollars=0,
            delivered=False
        )
    )
    print("  ✓ Pertenencias registradas")

# ── EVENTOS ────────────────────────────────────────────────────────────────────
print("Creando eventos...")
eventos_data = [
    dict(record=records[0], event_datetime=now - timedelta(days=2, hours=1),
         detention_datetime=now - timedelta(days=2),
         discriminator='falta', type='Conducta antisocial',
         subtype='Escandalo en via publica', violence='Sin violencia',
         detention_type='Flagrancia', reason='Altercado en via publica',
         arrested_by='Agente Garcia', place='Av. Juarez y 16 de septiembre',
         unit='Patrulla 45', sector='Centro', municipality='Juarez',
         country='Mexico', minimum_salaries=12, qualified_hours=36,
         qualifies=True, total_payable=0.0, created_by='JVALENZUELA'),
    dict(record=records[1], event_datetime=now - timedelta(days=1, hours=2),
         detention_datetime=now - timedelta(days=1),
         discriminator='falta', type='Conducta antisocial',
         subtype='Ebriedad', violence='Sin violencia',
         detention_type='Flagrancia', reason='Persona en estado de ebriedad',
         arrested_by='Agente Morales', place='Calle Reforma',
         unit='Patrulla 12', sector='Sur', municipality='Juarez',
         country='Mexico', minimum_salaries=6, qualified_hours=24,
         qualifies=True, total_payable=500.0, created_by='PMENDOZA'),
    dict(record=records[2], event_datetime=now - timedelta(hours=9),
         detention_datetime=now - timedelta(hours=8),
         discriminator='delito', type='Robo',
         subtype='Robo simple', violence='Con violencia',
         detention_type='Flagrancia', reason='Robo a transeunte',
         arrested_by='Agente Ramos', place='Blvd. Zaragoza',
         unit='Patrulla 78', sector='Oriente', municipality='Juarez',
         country='Mexico', minimum_salaries=0, qualified_hours=0,
         qualifies=False, total_payable=0.0, created_by='RGARCIA'),
]
for ev_data in eventos_data:
    ev, created = Events.objects.get_or_create(
        record=ev_data['record'],
        defaults=ev_data
    )
    if created:
        print(f"  ✓ Evento → {ev_data['record'].folio_afi}")

# ── REGISTROS MÉDICOS ──────────────────────────────────────────────────────────
print("Creando registros médicos...")
medicos_data = [
    dict(record=records[0], user=karsam,
         weight='75', height='1.72', intoxication='Ninguna',
         mental='Lúcido', general_condition='Bueno',
         medic_name='Dr. Carlos Ramírez', medical_cedula='12345678',
         medical_date_time=now - timedelta(days=2),
         pathologies='Ninguna', medical_t='36.5', medical_fc='72',
         medical_fr='16', medical_ta='120/80', saturation='98%',
         diagnostic='Sin lesiones aparentes', blood_type='O+',
         rh_factor='Positivo', has_lesions=False,
         created_by='karsam', folio='MED-001'),
    dict(record=records[1], user=karsam,
         weight='58', height='1.60', intoxication='Alcohol moderado',
         mental='Somnoliento', general_condition='Regular',
         medic_name='Dr. Carlos Ramírez', medical_cedula='12345678',
         medical_date_time=now - timedelta(days=1),
         pathologies='Ninguna', medical_t='36.8', medical_fc='88',
         medical_fr='18', medical_ta='110/70', saturation='97%',
         diagnostic='Intoxicación etílica leve', blood_type='A+',
         rh_factor='Positivo', has_lesions=False,
         created_by='karsam', folio='MED-002'),
    dict(record=records[2], user=karsam,
         weight='80', height='1.75', intoxication='Ninguna',
         mental='Agitado', general_condition='Regular',
         medic_name='Dr. Carlos Ramírez', medical_cedula='12345678',
         medical_date_time=now - timedelta(hours=7),
         pathologies='Ninguna', medical_t='37.1', medical_fc='95',
         medical_fr='20', medical_ta='130/85', saturation='99%',
         diagnostic='Excitación psicomotriz', blood_type='B+',
         rh_factor='Positivo', has_lesions=True,
         created_by='karsam', folio='MED-003'),
]
for med_data in medicos_data:
    med, created = MedicalInformation.objects.get_or_create(
        folio=med_data['folio'], defaults=med_data
    )
    if created:
        print(f"  ✓ Médico {med.folio} → {med_data['record'].folio_afi}")

# ── ACCIONES ───────────────────────────────────────────────────────────────────
print("Creando acciones legales...")
acciones_data = [
    dict(record=records[0], discriminator='remision',
         user='Usuario', action_folio='REM-2026-001',
         detainee='Juan Carlos Martínez López', age='34',
         nationality='Mexicana', district_name='Norte',
         date='2026-04-27', hour='05:00',
         article='25', fraction='I',
         agent1='Agente García', agent2='Agente López',
         unit='Patrulla 45', description='Escándalo en vía pública',
         has_ministerio_publico=False, has_iph=True,
         has_medical_certificate=True, has_car_inventory=False,
         action_date=now - timedelta(days=2)),
    dict(record=records[2], discriminator='puesta_disposicion',
         user='Usuario', action_folio='PD-2026-001',
         detainee='Roberto Sánchez Flores', age='26',
         nationality='Mexicana', district_name='Oriente',
         date='2026-04-27', hour='22:00',
         article='222', fraction='II',
         agent1='Agente Ramos', agent2='Agente Torres',
         unit='Patrulla 78', description='Robo a transeúnte con violencia',
         has_ministerio_publico=True, has_iph=True,
         has_medical_certificate=True, has_car_inventory=False,
         action_date=now - timedelta(hours=8)),
]
for acc_data in acciones_data:
    acc, created = Actions.objects.get_or_create(
        action_folio=acc_data['action_folio'], defaults=acc_data
    )
    if created:
        print(f"  ✓ Acción {acc.action_folio}")

# ── RESUMEN ────────────────────────────────────────────────────────────────────
print()
print("=" * 50)
print("RESUMEN FINAL")
print("=" * 50)
from detainees.models import Detainee
from records.models import Records, Cells, Events, MedicalInformation, Actions, Belongings
print(f"Distritos:         {District.objects.count()}")
print(f"Usuarios:          {User.objects.count()}")
print(f"Detenidos:         {Detainee.objects.count()}")
print(f"Expedientes:       {Records.objects.count()}")
print(f"Celdas asignadas:  {Cells.objects.count()}")
print(f"Eventos:           {Events.objects.count()}")
print(f"Registros médicos: {MedicalInformation.objects.count()}")
print(f"Pertenencias:      {Belongings.objects.count()}")
print(f"Acciones legales:  {Actions.objects.count()}")
print()
print("✅ Datos de prueba cargados exitosamente.")
