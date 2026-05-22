"""
seed_full.py — Completa datos faltantes y agrega registros relacionados realistas.
Uso: python manage.py shell < seed_full.py
"""
import os, django, random
from datetime import datetime, timedelta, timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'siprob.settings')
django.setup()

from django.contrib.auth import get_user_model
from detainees.models import Detainee
from records.models import Records, MedicalInformation, Cells, Actions, OtherRecords, District

User = get_user_model()
admin_user = User.objects.first()
district = District.objects.first()

# ── Helpers ────────────────────────────────────────────────────────────────────

def rnd_date(days_back_max=365 * 3):
    return datetime.now(timezone.utc) - timedelta(days=random.randint(1, days_back_max))

def rnd_datetime(start_days=30, end_days=0):
    start = datetime.now(timezone.utc) - timedelta(days=start_days)
    end   = datetime.now(timezone.utc) - timedelta(days=end_days)
    return start + (end - start) * random.random()

NICKNAMES = [
    'El Güero', 'La Sombra', 'El Rápido', 'Chivo', 'Pelón', 'El Tigre',
    'Borrego', 'El Chino', 'Morrión', 'La Bestia', 'Coyote', 'El Zurdo',
    'Patas', 'Tablas', 'El Gato', 'Garras', 'Culebra', 'Piraña',
]
OCCUPATIONS = [
    'Empleado', 'Comerciante', 'Albañil', 'Mecánico', 'Carpintero',
    'Electricista', 'Chofer', 'Estudiante', 'Desempleado', 'Campesino',
    'Vendedor ambulante', 'Mesero', 'Cocinero', 'Seguridad privada',
]
ETHNICITIES = ['Mestizo', 'Indígena', 'Afromexicano', None, None, None]
SCHOOLING   = ['Primaria', 'Secundaria', 'Preparatoria', 'Universidad', 'Sin estudios']
MARITAL     = ['Soltero', 'Casado', 'Divorciado', 'Viudo', 'Unión libre']
NATIONALITY = ['Mexicana', 'Mexicana', 'Mexicana', 'Estadounidense', 'Guatemalteca']
BLOOD_TYPES = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
CONDITIONS  = ['Bueno', 'Regular', 'Malo']
INTOX       = ['No', 'Alcohol', 'Drogas', 'Alcohol y drogas']
MENTAL      = ['Orientado', 'Desorientado', 'Agitado', 'Tranquilo']
BLOOD_PRES  = ['120/80', '110/70', '130/90', '140/95', '100/65']
CELLS_LIST  = ['Celda 1', 'Celda 2', 'Celda 3', 'Celda 4', 'Celda 5',
               'Celda Norte A', 'Celda Norte B', 'Celda Sur A', 'Celda Sur B']
AGENTS      = [
    ('Rodríguez García Carlos', '456', 'Unidad Norte'),
    ('Pérez Soto Mario', '789', 'Unidad Centro'),
    ('López Reyes Ana', '321', 'Unidad Sur'),
    ('Martínez Díaz José', '654', 'Patrulla 1'),
    ('González Ruiz Pedro', '987', 'Patrulla 2'),
]
INFRACTIONS = [
    ('Riña', '25', '1'), ('Escándalo', '30', '2'), ('Vandalismo', '32', '3'),
    ('Robo', '35', '1'), ('Amenazas', '40', '2'), ('Daño en propiedad', '28', '1'),
    ('Intoxicación pública', '22', '4'), ('Portación de arma', '50', '1'),
]
CRIMES      = [
    'Lesiones leves', 'Alteración del orden público', 'Robo a transeúnte',
    'Daño en propiedad ajena', 'Amenazas', 'Portación de arma blanca',
    'Resistencia a autoridad', 'Conducción bajo influencia del alcohol',
]
PROCESSES   = [
    'Falta administrativa', 'Delito menor', 'Arresto preventivo',
    'Investigación', 'Remisión ministerial',
]
SANCTIONS   = [
    'Arresto 36 horas', 'Arresto 24 horas', 'Arresto 48 horas',
    'Multa económica', 'Arresto 12 horas', 'Liberado sin cargos',
]
VEHICLE_BRANDS  = ['Nissan', 'Chevrolet', 'Ford', 'Toyota', 'Honda', 'Volkswagen', 'Dodge']
VEHICLE_MODELS  = ['Tsuru', 'Aveo', 'Focus', 'Corolla', 'Civic', 'Jetta', 'Charger']
VEHICLE_COLORS  = ['Blanco', 'Negro', 'Rojo', 'Azul', 'Gris', 'Plateado', 'Verde']
OBJECT_TYPES    = ['Teléfono celular', 'Mochila', 'Navaja', 'Cadena', 'Billetera', 'Droga']
ADDRESSES       = [
    'Av. Tecnológico 1234, Col. Centro', 'Calle Juárez 567, Col. Bellavista',
    'Blvd. Independencia 890, Col. Los Nogales', 'Calle Morelos 321, Col. San Felipe',
    'Av. Insurgentes 654, Col. Partido Romero', 'Calle Lerdo 987, Col. Chaveña',
]

# ── 1. Completar campos vacíos en Detainee ─────────────────────────────────────
print('Completando Detainee...')
for d in Detainee.objects.all():
    changed = False
    if not d.nicknames:
        d.nicknames = random.choice(NICKNAMES) if random.random() > 0.4 else None
        changed = True
    if not d.marital_status:
        d.marital_status = random.choice(MARITAL)
        changed = True
    if not d.ethnicity:
        d.ethnicity = random.choice(ETHNICITIES)
        changed = True
    if not d.nationality:
        d.nationality = random.choice(NATIONALITY)
        changed = True
    if not d.schooling:
        d.schooling = random.choice(SCHOOLING)
        changed = True
    if not d.occupation:
        d.occupation = random.choice(OCCUPATIONS)
        changed = True
    if changed:
        d.save()
print(f'  → {Detainee.objects.count()} detenidos actualizados')

# ── 2. Completar campos vacíos en Records ─────────────────────────────────────
print('Completando Records...')
for rec in Records.objects.all():
    changed = False
    if not rec.process:
        rec.process = random.choice(PROCESSES)
        changed = True
    if not rec.sanction:
        rec.sanction = random.choice(SANCTIONS)
        changed = True
    if not rec.notes:
        rec.notes = random.choice([
            'Sin novedad al ingreso', 'Cooperativo durante el proceso',
            'Presentó resistencia al arresto', 'Ingresó con lesiones visibles',
            'Solicita comunicarse con familiar', None, None,
        ])
        changed = True
    if not rec.fundament:
        rec.fundament = random.randint(20, 50)
        changed = True
    if changed:
        rec.save()
print(f'  → {Records.objects.count()} registros actualizados')

# ── 3. Crear MedicalInformation faltante ─────────────────────────────────────
print('Creando MedicalInformation faltante...')
records_without_med = Records.objects.filter(medicalinformation__isnull=True)
created_med = 0
for rec in records_without_med:
    MedicalInformation.objects.create(
        record=rec,
        folio=f'MED-{rec.id:04d}',
        weight=round(random.uniform(55, 110), 1),
        height=round(random.uniform(1.55, 1.90), 2),
        intoxication=random.choice(INTOX),
        mental=random.choice(MENTAL),
        general_condition=random.choice(CONDITIONS),
        medic_name=random.choice([
            'Dr. Hernández Soto', 'Dra. Ramírez Cruz', 'Dr. Valdez Moreno',
            'Dra. Jiménez Leal', 'Dr. Torres Bernal',
        ]),
        medical_date_time=rec.entry_date + timedelta(hours=random.randint(1, 3)),
        pathologies=random.choice(['Ninguna', 'Diabetes', 'Hipertensión', 'Ninguna', 'Asma']),
        user=admin_user,
        medical_t=round(random.uniform(36.0, 37.8), 1),
        medical_fc=random.randint(60, 100),
        medical_fr=random.randint(12, 20),
        medical_ta=random.choice(BLOOD_PRES),
        saturation=random.randint(94, 100),
        diagnostic=random.choice([
            'Paciente estable', 'Sin lesiones aparentes', 'Lesiones leves en extremidades',
            'Estado de ebriedad moderada', 'Herida superficial en mano derecha',
        ]),
        blood_type=random.choice(BLOOD_TYPES),
        rh_factor=random.choice(['Positivo', 'Negativo']),
        has_lesions=random.choice([True, False, False]),
        is_active=True,
        created_at=rec.entry_date + timedelta(hours=random.randint(1, 3)),
    )
    created_med += 1
print(f'  → {created_med} registros médicos creados')

# ── 4. Crear Cells faltante ────────────────────────────────────────────────────
print('Creando Cells faltante...')
records_without_cell = Records.objects.filter(cells__isnull=True)
created_cells = 0
for rec in records_without_cell:
    Cells.objects.create(
        record=rec,
        cell=random.choice(CELLS_LIST),
        cell_notes=random.choice([
            None, 'Sin novedad', 'Requiere vigilancia especial',
            'Separado de otros internos', 'Solicita agua',
        ]),
        registered_belongings=random.choice([True, False]),
        registered_calls=random.choice([True, False]),
        total_belongings=random.randint(0, 8),
        total_calls=random.randint(0, 3),
        is_active=True,
        created_at=rec.entry_date + timedelta(hours=random.randint(2, 5)),
    )
    created_cells += 1
print(f'  → {created_cells} celdas creadas')

# ── 5. Crear Actions para todos los registros ─────────────────────────────────
print('Creando Actions...')
records_without_action = Records.objects.filter(actions__isnull=True)
created_actions = 0
for rec in records_without_action:
    agent = random.choice(AGENTS)
    infraction = random.choice(INFRACTIONS)
    action_dt = rec.entry_date - timedelta(hours=random.randint(1, 4))
    Actions.objects.create(
        record=rec,
        detainee=rec.detainee,
        discriminator='PD',
        action_folio=f'ACT-{rec.id:04d}',
        date=action_dt.strftime('%Y-%m-%d'),
        hour=action_dt.strftime('%H:%M'),
        action_date=action_dt,
        age=rec.detainee.age or random.randint(18, 60),
        nationality=rec.detainee.nationality or 'Mexicana',
        address=random.choice(ADDRESSES),
        article=infraction[1],
        fraction=infraction[2],
        infraction_number=str(random.randint(100, 999)),
        unit=agent[2],
        agent1=agent[0],
        agent2=random.choice(AGENTS)[0],
        agent_name=agent[0],
        agent_job='Oficial de Seguridad',
        agent_number=agent[1],
        agent_unit=agent[2],
        crime=random.choice(CRIMES),
        description=random.choice([
            'Persona detenida en la vía pública en estado de alteración.',
            'Detenido por riña en establecimiento comercial.',
            'Aprehendido por daños a propiedad ajena.',
            'Detenido por portación de arma blanca.',
            'Detenido por robo a transeúnte.',
        ]),
        district_name=district.name if district else 'Norte',
        remission=rec.folio_afi,
        has_ministerio_publico=random.choice([True, False]),
        has_iph=random.choice([True, False]),
        has_chain_custody=random.choice([True, False]),
        has_medical_certificate=random.choice([True, False]),
        has_car_inventory=False,
        is_active=True,
        created_at=rec.entry_date,
    )
    created_actions += 1
print(f'  → {created_actions} actuaciones creadas')

# ── 6. Crear OtherRecords ──────────────────────────────────────────────────────
print('Creando OtherRecords...')
created_other = 0
if district:
    for i in range(1, 31):
        is_vehicle = random.random() > 0.45
        dt = rnd_datetime(90, 0)
        if is_vehicle:
            brand = random.choice(VEHICLE_BRANDS)
            model = random.choice(VEHICLE_MODELS)
            color = random.choice(VEHICLE_COLORS)
            OtherRecords.objects.create(
                district=district,
                discriminator='vehicle',
                other_record_folio=f'VEH-{i:04d}',
                date=dt,
                detention_type='Remisión',
                place=random.choice(ADDRESSES),
                holder_name=f'{random.choice(["Carlos","Ana","Luis","María","José"])} {random.choice(["Pérez","García","López","Martínez","Rodríguez"])}',
                vehicle_type=random.choice(['Automóvil', 'Camioneta', 'Motocicleta']),
                brand=brand,
                line=model,
                model=str(random.randint(2005, 2023)),
                color=color,
                plates=f'{random.choice(["ABC","XYZ","DEF","GHI"])}{random.randint(100,9999)}',
                serial_number=f'SN{random.randint(10000,99999)}',
                general_condition=random.choice(CONDITIONS),
                comments=random.choice([None, 'Sin novedad', 'Cristales rotos', 'Sin placas originales']),
                is_active=True,
                created_at=dt,
            )
        else:
            OtherRecords.objects.create(
                district=district,
                discriminator='object',
                other_record_folio=f'OBJ-{i:04d}',
                date=dt,
                detention_type='Remisión',
                place=random.choice(ADDRESSES),
                holder_name=f'{random.choice(["Carlos","Ana","Luis","María","José"])} {random.choice(["Pérez","García","López","Martínez","Rodríguez"])}',
                type=random.choice(OBJECT_TYPES),
                description=random.choice([
                    'En buen estado', 'Deteriorado', 'Con indicios de uso',
                    'Marca no identificada', 'Sin características especiales',
                ]),
                quantity=random.randint(1, 5),
                general_condition=random.choice(CONDITIONS),
                comments=None,
                is_active=True,
                created_at=dt,
            )
        created_other += 1
print(f'  → {created_other} otros registros creados (vehículos/objetos)')

# ── Resumen ────────────────────────────────────────────────────────────────────
print('\n=== SEED COMPLETO ===')
print(f'Detainees:       {Detainee.objects.count()}')
print(f'Records:         {Records.objects.count()}')
print(f'MedicalInfo:     {MedicalInformation.objects.count()}')
print(f'Cells:           {Cells.objects.count()}')
print(f'Actions:         {Actions.objects.count()}')
print(f'OtherRecords:    {OtherRecords.objects.count()}')
