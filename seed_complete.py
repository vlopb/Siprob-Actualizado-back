"""
seed_complete.py — Rellena TODOS los campos posibles en todos los modelos.
Uso: python manage.py shell < seed_complete.py
"""
import os, django, random
from datetime import datetime, timedelta, timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'siprob.settings')
django.setup()

from django.contrib.auth import get_user_model
from detainees.models import Detainee
from records.models import (
    Records, MedicalInformation, Cells, Actions, ActionNotes,
    OtherRecords, OtherRecordsDetainees, Events,
    Belongings, CallsRegistry, Lesions, RecordsPoliceAgents, District
)

User = get_user_model()
admin_user = User.objects.first()
district = District.objects.first()

# ── Catálogos ───────────────────────────────────────────────────────────────────

NOMBRES_M = ['Carlos','Miguel','José','Luis','Juan','Roberto','Fernando','Alejandro','Eduardo','Ricardo','Sergio','Marco','Diego','Adrián','Iván','Raúl','Héctor','Arturo','Ernesto','Gerardo']
NOMBRES_F = ['María','Ana','Laura','Claudia','Patricia','Verónica','Gabriela','Rosa','Leticia','Sandra','Alejandra','Norma','Carmen','Lucía','Elena','Silvia','Mónica','Guadalupe','Beatriz','Alicia']
APELLIDOS_P = ['García','Martínez','López','Rodríguez','González','Pérez','Sánchez','Ramírez','Torres','Flores','Rivera','Morales','Ortiz','Reyes','Cruz','Vargas','Castillo','Herrera','Jiménez','Mendoza']
APELLIDOS_M = ['Vega','Ramos','Luna','Silva','Guerrero','Medina','Aguilar','Rojas','Delgado','Castro','Núñez','Alvarez','Ruiz','Gutiérrez','Ríos','Espinoza','Cabrera','Navarro','Acosta','Fuentes']

PHONES = lambda: f'656{random.randint(1000000,9999999)}'
ADDRESSES = [
    'Av. Tecnológico 1234, Col. Centro', 'Calle Juárez 567, Col. Bellavista',
    'Blvd. Independencia 890, Col. Los Nogales', 'Calle Morelos 321, Col. San Felipe',
    'Av. Insurgentes 654, Col. Partido Romero', 'Calle Lerdo 987, Col. Chaveña',
    'Av. De las Torres 456, Col. Fronteriza', 'Calle Bravo 123, Col. Centro',
    'Blvd. Zaragoza 789, Col. Aztecas', 'Calle Noche Buena 321, Col. Las Granjas',
]
COLONIAS = ['Col. Centro','Col. Bellavista','Col. Los Nogales','Col. San Felipe','Col. Partido Romero','Col. Chaveña','Col. Aztecas','Col. Las Granjas','Col. Fronteriza','Col. Melchor Ocampo']
CALLES = ['Av. Tecnológico','Calle Juárez','Blvd. Independencia','Calle Morelos','Av. Insurgentes','Calle Lerdo','Av. De las Torres','Calle Bravo','Blvd. Zaragoza','Calle Noche Buena']
MUNICIPIOS = ['Juárez','Chihuahua','Delicias','Cuauhtémoc','Parral']
SECTORES = ['Norte','Sur','Centro','Oriente','Poniente']
UNIDADES = ['Patrulla 01','Patrulla 02','Patrulla 03','Unidad Norte','Unidad Sur','Unidad Centro','Radio Patrulla 07']
ARRESTED_BY = ['Policía Municipal','Policía Estatal','Guardia Nacional','Policía Vial','Policía de Proximidad']
LESION_LOCATIONS = ['Mano derecha','Mano izquierda','Brazo derecho','Brazo izquierdo','Pierna derecha','Pierna izquierda','Rostro','Tórax','Espalda','Cabeza']
LESION_TYPES = ['contusion','abrasion','herida','fractura','luxacion']
LESION_DESC = ['Hematoma de 3 cm','Abrasión superficial','Laceración leve','Equimosis sin edema','Herida contusa']
RELATIONSHIPS = ['Esposa','Esposo','Madre','Padre','Hermano','Hermana','Hijo','Hija','Amigo','Pareja']
AFFINITY = ['Cónyuge','Familiar','Amigo','Conocido','Ninguno']
IDS = ['INE','Pasaporte','Licencia de conducir','Credencial de trabajo','Sin identificación']
RELEASE_TYPES = ['Libertad simple','Libertad bajo fianza','Remisión a MP','Cumplimiento de sanción','Liberado por orden judicial']
RELEASE_REASONS = ['Cumplió sanción','Orden judicial','Fianza cubierta','Sin cargos','Entrega a familiar responsable']
AMBIENT = ['Calle','Establecimiento','Domicilio','Unidad vehicular','Transporte público','Lugar baldío']
VIOLENCE = ['Sin violencia','Con violencia','Con arma blanca','Con violencia verbal']
MODUS = ['Sorpresivo','Premeditado','Bajo influencia de alcohol','En riña','Solo']
CLASIF = ['Detención preventiva','Remisión directa','Aprehensión','Presentación voluntaria']
EMPLOYEE_NUMBERS = [f'EMP-{i:04d}' for i in range(1, 50)]
EVENT_TYPES_MAP = {
    'records': ['detention','release','transfer'],
    'others':  ['vehicle_entry','object_entry'],
}
SUBTYPE_MAP = {
    'detention': ['administrative','criminal'],
    'release':   ['completed','judicial','bail'],
    'transfer':  ['internal','external'],
}

def rnd_name_m(): return f'{random.choice(NOMBRES_M)} {random.choice(APELLIDOS_P)} {random.choice(APELLIDOS_M)}'
def rnd_name_f(): return f'{random.choice(NOMBRES_F)} {random.choice(APELLIDOS_P)} {random.choice(APELLIDOS_M)}'
def rnd_name(): return rnd_name_m() if random.random() > 0.4 else rnd_name_f()
def rnd_dt_offset(base, min_h=1, max_h=6): return base + timedelta(hours=random.randint(min_h, max_h))

# ── 1. Completar Detainee (campos opcionales restantes) ──────────────────────
print('1. Completando Detainee...')
updated = 0
for d in Detainee.objects.all():
    changed = False
    if not d.fake_names:
        d.fake_names = rnd_name() if random.random() > 0.6 else None
        changed = True
    if not d.sexual_preferences:
        d.sexual_preferences = random.choice(['Heterosexual','Homosexual','Bisexual',None,None,None])
        changed = True
    if not d.notes:
        d.notes = random.choice([
            None,'Sin antecedentes previos','Reincidente','Conocido por las autoridades',
            'Primera detención','Antecedentes en otra delegación', None,
        ])
        changed = True
    if changed:
        d.save()
        updated += 1
print(f'   {updated} detenidos actualizados')

# ── 2. Completar Records (campos de liberación para ~40%) ──────────────────────
print('2. Completando Records...')
updated = 0
records = list(Records.objects.all())
released_sample = random.sample(records, k=int(len(records) * 0.4))
for rec in records:
    changed = False
    if rec in released_sample and not rec.has_been_released:
        rec.has_been_released = True
        rec.release_type = random.choice(RELEASE_TYPES)
        rec.release_reason = random.choice(RELEASE_REASONS)
        rec.official_release_date = rnd_dt_offset(rec.entry_date, 12, 60)
        rec.qualification_release_date = rnd_dt_offset(rec.entry_date, 8, 48)
        rec.is_active = False
        changed = True
    if not rec.release_important_cell_note and random.random() > 0.7:
        rec.release_important_cell_note = random.choice([
            'Sin incidentes durante la detención','Requirió atención médica',
            'Solicitó comunicarse con abogado','Se le entregaron sus pertenencias completas',
        ])
        changed = True
    if changed:
        rec.save()
        updated += 1
print(f'   {updated} registros actualizados')

# ── 3. Completar Cells (campos faltantes) ────────────────────────────────────
print('3. Completando Cells...')
updated = 0
for cell in Cells.objects.all():
    changed = False
    if not cell.assignment_folio:
        cell.assignment_folio = f'ASIG-{cell.id:04d}'
        changed = True
    if not cell.registered_by:
        cell.registered_by = admin_user.username
        changed = True
    if not cell.created_by:
        cell.created_by = admin_user.username
        changed = True
    if changed:
        cell.save()
        updated += 1
print(f'   {updated} celdas actualizadas')

# ── 4. Completar Actions (campos opcionales) ──────────────────────────────────
print('4. Completando Actions...')
updated = 0
for action in Actions.objects.all():
    changed = False
    if not action.relative:
        action.relative = rnd_name()
        action.relative_age = random.randint(18, 70)
        action.affinity = random.choice(AFFINITY)
        changed = True
    if not action.identification:
        action.identification = random.choice(IDS)
        action.id_number = f'{random.randint(100000000, 999999999)}'
        changed = True
    if not action.address:
        action.address = random.choice(ADDRESSES)
        changed = True
    if not action.victim:
        action.victim = rnd_name() if random.random() > 0.5 else None
        changed = True
    if not action.other:
        action.other = random.choice([None, 'Ninguno', 'Se decomisaron objetos', None])
        changed = True
    if not action.subject:
        action.subject = random.choice(['Director de Seguridad Pública','Jefe de Turno','Coordinador de Área'])
        action.subject_to = random.choice(['Dirección General','Jefatura de Sector','Comando Norte'])
        action.written_to = random.choice(['Juez Cívico Turno Matutino','Juez Cívico Turno Vespertino','Ministerio Público'])
        changed = True
    if not action.office_number:
        action.office_number = f'OF-{random.randint(100,999)}/{datetime.now().year}'
        changed = True
    if action.money_mexican_pesos is None:
        action.money_mexican_pesos = random.choice([0, 0, 50, 120, 350, 500, 0])
        action.money_american_dollars = random.choice([0, 0, 0, 20, 0])
        changed = True
    if changed:
        action.save()
        updated += 1
print(f'   {updated} actuaciones actualizadas')

# ── 5. Completar Events (campos de geolocalización y clasificación) ───────────
print('5. Completando Events...')
updated = 0
for ev in Events.objects.all():
    changed = False
    if not ev.place:
        ev.place = random.choice(ADDRESSES)
        changed = True
    if not ev.unit:
        ev.unit = random.choice(UNIDADES)
        changed = True
    if not ev.sector:
        ev.sector = random.choice(SECTORES)
        changed = True
    if not ev.arrested_by:
        ev.arrested_by = random.choice(ARRESTED_BY)
        changed = True
    if not ev.ambient:
        ev.ambient = random.choice(AMBIENT)
        changed = True
    if not ev.violence:
        ev.violence = random.choice(VIOLENCE)
        changed = True
    if not ev.modus_operandi:
        ev.modus_operandi = random.choice(MODUS)
        changed = True
    if not ev.clasification:
        ev.clasification = random.choice(CLASIF)
        changed = True
    if not ev.locality:
        ev.locality = 'Ciudad Juárez'
        changed = True
    if not ev.municipality:
        ev.municipality = random.choice(MUNICIPIOS)
        changed = True
    if not ev.country:
        ev.country = 'México'
        changed = True
    if not ev.street:
        ev.street = random.choice(CALLES)
        ev.exterior_number = str(random.randint(1, 2000))
        ev.interior_number = str(random.randint(1, 20)) if random.random() > 0.7 else ''
        ev.colony = random.choice(COLONIAS)
        ev.cross_street = random.choice(CALLES)
        changed = True
    if not ev.event_description:
        ev.event_description = random.choice([
            'El detenido fue encontrado en la vía pública en estado de alteración.',
            'Riña entre dos personas en establecimiento comercial.',
            'Persona reportada por vecinos por conducta escandalosa.',
            'Detenido intentando sustraer mercancía de local comercial.',
            'Persona encontrada en posesión de objeto robado.',
            'Detenido por agresión verbal y física a transeúnte.',
        ])
        changed = True
    if not ev.reason:
        ev.reason = random.choice([
            'Falta administrativa','Alteración del orden','Riña','Robo','Escándalo en vía pública',
        ])
        changed = True
    if not ev.detention_type:
        ev.detention_type = random.choice(['Aprehensión','Presentación','Remisión'])
        changed = True
    if ev.minimum_salaries is None:
        ev.minimum_salaries = random.randint(1, 36)
        changed = True
    if ev.qualified_hours is None:
        ev.qualified_hours = random.choice([12, 24, 36, 48, 0])
        changed = True
    if changed:
        ev.save()
        updated += 1
print(f'   {updated} eventos actualizados')

# ── 6. Crear Belongings para todas las celdas ─────────────────────────────────
print('6. Creando Belongings...')
cells_without = Cells.objects.filter(belongings__isnull=True)
created = 0
for cell in cells_without:
    has_phone  = random.random() > 0.3
    has_wallet = random.random() > 0.4
    has_keys   = random.random() > 0.5
    has_belt   = random.random() > 0.6
    has_shoes  = random.random() > 0.2
    Belongings.objects.create(
        cell=cell,
        registration_datetime=rnd_dt_offset(cell.created_at, 0, 2),
        document_ine=random.choice([True, False]),
        document_mexican_passport=random.choice([True, False, False]),
        document_american_passport=False,
        document_residence=False,
        document_other=random.choice([True, False, False]),
        document_notes=random.choice([None,'Copia fotostática','Original','Vencida']) if random.random()>0.5 else None,
        jewelry_earrings=random.choice([True, False, False]),
        jewelry_ring=random.choice([True, False, False]),
        jewelry_chain=random.choice([True, False]),
        jewelry_bracelet=random.choice([True, False, False]),
        jewelry_clock=random.choice([True, False]),
        jewelry_other=False,
        jewelry_notes=None,
        devices_cellphone=has_phone,
        devices_charger=has_phone and random.random() > 0.5,
        devices_laptop=False,
        devices_cables=random.choice([True, False, False]),
        devices_aux=False,
        devices_tablet=False,
        devices_usb=False,
        devices_computer_equipment=False,
        devices_keys=has_keys,
        devices_notes=random.choice([None,'Samsung Galaxy','iPhone 12','Motorola']) if has_phone else None,
        accesories_cap=random.choice([True, False]),
        accesories_ribbons=False,
        accesories_shoes=has_shoes,
        accesories_backpack=random.choice([True, False, False]),
        accesories_sunglasses=random.choice([True, False, False]),
        accesories_cigarettes=random.choice([True, False, False]),
        accesories_belt=has_belt,
        accesories_handbag=False,
        accesories_other=False,
        accesories_notes=None,
        money_mexican_pesos=random.choice([0, 0, 50, 120, 350, 500]),
        money_american_dollars=random.choice([0, 0, 0, 20]),
        bank_cards=random.choice([True, False, False]),
        delivered=random.choice([True, False]),
        delivered_to_another=False,
        delivery_notes=random.choice([None,'Entregado sin incidentes','Firmó de recibido']) if random.random()>0.5 else None,
        delivery_relationship=random.choice(RELATIONSHIPS) if random.random()>0.5 else None,
        remission=cell.record.folio_afi if hasattr(cell, 'record') else None,
        is_active=True,
    )
    created += 1
print(f'   {created} pertenencias creadas')

# ── 7. Crear CallsRegistry para celdas con llamadas registradas ───────────────
print('7. Creando CallsRegistry...')
created = 0
for cell in Cells.objects.filter(registered_calls=True):
    for _ in range(random.randint(1, cell.total_calls or 1)):
        CallsRegistry.objects.create(
            cell=cell,
            call_datetime=rnd_dt_offset(cell.created_at, 2, 24),
            had_response=random.choice([True, True, False]),
            accepted=random.choice([True, True, False]),
            user=admin_user,
            name=rnd_name(),
            phone_number=PHONES(),
            detainee_relationship=random.choice(RELATIONSHIPS),
            is_active=True,
        )
        created += 1
print(f'   {created} llamadas registradas')

# ── 8. Crear Lesions para registros médicos con lesiones ───────────────────────
print('8. Creando Lesions...')
created = 0
for med in MedicalInformation.objects.filter(has_lesions=True):
    for _ in range(random.randint(1, 3)):
        Lesions.objects.create(
            medical_information=med,
            location=random.choice(LESION_LOCATIONS),
            discriminator=random.choice(LESION_TYPES),
            description=random.choice(LESION_DESC),
            notes=random.choice([None,'Lesión previa','Reciente','En proceso de sanación']),
            is_active=True,
        )
        created += 1
print(f'   {created} lesiones registradas')

# ── 9. Crear RecordsPoliceAgents para todos los records ───────────────────────
print('9. Creando RecordsPoliceAgents...')
all_users = list(User.objects.all())
existing_records = set(RecordsPoliceAgents.objects.values_list('record_id', flat=True))
created = 0
for rec in Records.objects.exclude(id__in=existing_records):
    RecordsPoliceAgents.objects.create(
        employee_number=random.choice(all_users),
        record=rec,
        is_active=True,
    )
    created += 1
print(f'   {created} agentes asignados a registros')

# ── 10. Crear ActionNotes para ~50% de las actuaciones ────────────────────────
print('10. Creando ActionNotes...')
created = 0
actions_sample = random.sample(list(Actions.objects.all()), k=Actions.objects.count() // 2)
for action in actions_sample:
    ActionNotes.objects.create(
        action=action,
        user=admin_user,
        text=random.choice([
            'El detenido mostró cooperación durante el proceso.',
            'Se requirió apoyo adicional para el traslado.',
            'El detenido solicitó asistencia médica.',
            'Sin novedad durante el turno.',
            'Se notificó a familiar responsable.',
            'El detenido se negó a firmar el documento.',
            'Se realizó revisión corporal sin incidentes.',
            'El detenido presentó documentos de identificación.',
        ]),
        is_active=True,
        created_at=action.created_at + timedelta(minutes=random.randint(5, 120)),
    )
    created += 1
print(f'   {created} notas de actuación creadas')

# ── 11. Crear OtherRecordsDetainees (vincular otros registros con detenidos) ──
print('11. Creando OtherRecordsDetainees...')
created = 0
detainee_ids = list(Detainee.objects.values_list('id', flat=True))
for other in OtherRecords.objects.filter(otherrecordsdetainees__isnull=True)[:20]:
    OtherRecordsDetainees.objects.create(
        other_record=other,
        detainee_id=random.choice(detainee_ids),
        is_active=True,
    )
    created += 1
print(f'   {created} vínculos otrosRegistros-detenido creados')

# ── Resumen final ──────────────────────────────────────────────────────────────
print('\n=== SEED COMPLETO ===')
from records.models import Belongings, CallsRegistry, Lesions, RecordsPoliceAgents, ActionNotes, Events, OtherRecordsDetainees
print(f'Detainees:              {Detainee.objects.count()}')
print(f'Records:                {Records.objects.count()}')
print(f'  → liberados:          {Records.objects.filter(has_been_released=True).count()}')
print(f'MedicalInformation:     {MedicalInformation.objects.count()}')
print(f'  → con lesiones:       {MedicalInformation.objects.filter(has_lesions=True).count()}')
print(f'Cells:                  {Cells.objects.count()}')
print(f'Belongings:             {Belongings.objects.count()}')
print(f'CallsRegistry:          {CallsRegistry.objects.count()}')
print(f'Lesions:                {Lesions.objects.count()}')
print(f'Actions:                {Actions.objects.count()}')
print(f'ActionNotes:            {ActionNotes.objects.count()}')
print(f'Events:                 {Events.objects.count()}')
print(f'RecordsPoliceAgents:    {RecordsPoliceAgents.objects.count()}')
print(f'OtherRecords:           {OtherRecords.objects.count()}')
print(f'OtherRecordsDetainees:  {OtherRecordsDetainees.objects.count()}')
