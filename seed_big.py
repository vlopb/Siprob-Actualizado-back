import os, sys, random
sys.path.insert(0, '/usr/src/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from django.utils import timezone
from datetime import timedelta, date
from districts.models import District
from users.models import User
from detainees.models import Detainee, Phones, Addresses
from records.models import Records, Cells, Events, MedicalInformation, Belongings, Actions

random.seed(42)
now = timezone.now()

norte    = District.objects.get(name='Norte')
sur      = District.objects.get(name='Sur')
oriente  = District.objects.get(name='Oriente')
poniente = District.objects.get(name='Poniente')
distritos = [norte, sur, oriente, poniente]
karsam = User.objects.get(username='karsam')

nombres_m = ['Juan','Carlos','Luis','Miguel','Pedro','Jorge','Antonio','Francisco','Roberto','Manuel','David','Jose','Eduardo','Ricardo','Fernando','Alejandro','Victor','Hector','Gabriel','Diego','Mario','Oscar','Raul','Ernesto','Arturo','Marco','Ivan','Sergio','Andres','Daniel','Pablo','Alfredo','Alberto','Rafael','Enrique','Gustavo','Javier','Ruben','Adrian','Cesar']
nombres_f = ['Maria','Ana','Rosa','Patricia','Laura','Sofia','Claudia','Gabriela','Monica','Adriana','Veronica','Carmen','Diana','Lupita','Elizabeth','Sandra','Norma','Cristina','Alejandra','Beatriz','Silvia','Martha','Yolanda','Leticia','Margarita','Jessica','Paola','Nancy','Irma','Gloria']
apellidos = ['Garcia','Martinez','Lopez','Hernandez','Gonzalez','Perez','Sanchez','Ramirez','Torres','Flores','Rivera','Gomez','Diaz','Reyes','Morales','Cruz','Ortiz','Gutierrez','Chavez','Ramos','Medina','Aguilar','Castillo','Jimenez','Vargas','Romero','Salinas','Mendez','Ruiz','Alvarez','Moreno','Delgado','Vega','Soto','Castro','Cabrera','Avila','Rios','Carrillo','Lara','Nunez','Munoz','Pena','Herrera','Contreras','Fuentes','Guerrero','Mendoza','Suarez','Velasquez']
ocupaciones_m = ['Empleado','Comerciante','Estudiante','Desempleado','Obrero','Vendedor','Conductor','Mecanico','Albanil','Carpintero','Electricista','Plomero','Cocinero','Mesero','Seguridad','Agricultor','Chofer','Repartidor','Pintor','Jardinero']
ocupaciones_f = ['Empleada','Comerciante','Estudiante','Desempleada','Obrera','Vendedora','Cocinera','Mesera','Enfermera','Maestra','Secretaria','Ama de casa','Costurera','Estilista','Cajera','Enfermera','Asistente','Operadora']
escolaridades = ['Primaria','Secundaria','Preparatoria','Universidad','Sin estudios','Tecnico']
estados_m = ['Soltero','Casado','Divorciado','Union libre','Viudo']
estados_f = ['Soltera','Casada','Divorciada','Union libre','Viuda']
tipos_sangre = ['A+','A-','B+','B-','O+','O-','AB+','AB-']
unidades = ['Patrulla 12','Patrulla 23','Patrulla 34','Patrulla 45','Patrulla 56','Patrulla 67','Patrulla 78','Patrulla 89','Patrulla 90','Moto 05','Moto 07','Moto 11']
agentes_lista = ['Agente Garcia','Agente Lopez','Agente Martinez','Agente Sanchez','Agente Torres','Agente Ramirez','Agente Flores','Agente Morales','Agente Reyes','Agente Cruz','Agente Gomez','Agente Diaz','Agente Vargas','Agente Castillo','Agente Herrera']
sectores = ['Centro','Norte','Sur','Oriente','Poniente','Nororiente','Norponiente','Suroriente','Surponiente']
colonias = ['Centro','Division del Norte','Revolucion','Independencia','Hidalgo','Morelos','Las Torres','Anaya','Partido Romero','Chaveña','Salvarcar','San Lorenzo','Rancho Anapra','Fronteriza','Zaragoza']
vias = ['Av.','Calle','Blvd.','Paseo','Circuito']
tipos_delito = [
    ('falta','Conducta antisocial','Escandalo en via publica','Sin violencia', 0, 24),
    ('falta','Conducta antisocial','Ebriedad','Sin violencia', 0, 24),
    ('falta','Conducta antisocial','Rina','Sin violencia', 0, 36),
    ('falta','Conducta antisocial','Danos a propiedad','Sin violencia', 6, 48),
    ('falta','Conducta antisocial','Ingestion de alcohol en via publica','Sin violencia', 0, 12),
    ('falta','Conducta antisocial','Desobediencia a autoridad','Sin violencia', 3, 24),
    ('falta','Conducta antisocial','Uso de lenguaje obsceno','Sin violencia', 0, 12),
    ('falta','Conducta antisocial','Grafiti','Sin violencia', 4, 36),
    ('delito','Robo','Robo simple','Sin violencia', 0, 0),
    ('delito','Robo','Robo con violencia','Con violencia', 0, 0),
    ('delito','Robo','Robo a negocio','Con violencia', 0, 0),
    ('delito','Robo','Robo de vehiculo','Sin violencia', 0, 0),
    ('delito','Lesiones','Lesiones dolosas','Con violencia', 0, 0),
    ('delito','Violencia familiar','Violencia fisica','Con violencia', 0, 0),
    ('delito','Posesion de drogas','Posesion simple','Sin violencia', 0, 0),
    ('delito','Posesion de drogas','Posesion con fines de distribucion','Sin violencia', 0, 0),
    ('delito','Amenazas','Amenazas verbales','Sin violencia', 0, 0),
]
sanciones_falta = ['Arresto 12 horas','Arresto 24 horas','Arresto 36 horas','Arresto 48 horas','Multa','Amonestacion','Trabajo comunitario 8 horas','Trabajo comunitario 16 horas']
sanciones_delito = ['Puesta a disposicion','Remision MP','Puesta a disposicion MP']
diagnosticos_sin_lesion = ['Sin lesiones aparentes','Sin alteraciones','Estado general bueno','Sin lesiones visibles']
diagnosticos_con_lesion = ['Contusion leve','Excoriaciones multiples','Herida superficial','Traumatismo craneal leve','Equimosis en extremidades','Hematoma facial','Laceración leve']
patologias = ['Ninguna','Ninguna','Ninguna','Ninguna','Hipertension','Diabetes tipo 2','Asma','Epilepsia']

print("Generando 100 detenidos con expedientes completos...")

for i in range(100):
    genero = random.choice(['Masculino','Femenino'])
    if genero == 'Masculino':
        nombre = random.choice(nombres_m)
        est_civil = random.choice(estados_m)
        ocup = random.choice(ocupaciones_m)
    else:
        nombre = random.choice(nombres_f)
        est_civil = random.choice(estados_f)
        ocup = random.choice(ocupaciones_f)

    ap1 = random.choice(apellidos)
    ap2 = random.choice(apellidos)
    edad = random.randint(18, 65)
    bd = date(2024 - edad, random.randint(1, 12), random.randint(1, 28))

    # Usar sufijo para evitar duplicados por nombre+apellido
    suffix = f' {chr(65 + i // 26)}{i:02d}' if i >= 26 else ''
    det, _ = Detainee.objects.get_or_create(
        name=nombre + suffix,
        fathers_name=ap1,
        mothers_name=ap2,
        defaults=dict(
            birth_date=bd, age=edad, gender=genero,
            marital_status=est_civil, nationality='Mexicana',
            occupation=ocup, schooling=random.choice(escolaridades),
            is_active=True
        )
    )

    if random.random() > 0.35:
        Phones.objects.get_or_create(
            detainee=det,
            phone_number=f'656{random.randint(1000000,9999999)}',
            defaults={'description': 'Personal'}
        )

    # Expediente
    dias_atras = random.randint(0, 120)
    horas_atras = random.randint(0, 23)
    entry = now - timedelta(days=dias_atras, hours=horas_atras)
    liberado = random.random() > 0.40
    folio = f'AFI-2026-{200+i:03d}'
    distrito = random.choice(distritos)
    tipo = random.choice(tipos_delito)
    discriminador, tipo_ev, subtipo_ev, violencia_ev, min_sal, hrs_cal = tipo
    sancion = random.choice(sanciones_falta) if discriminador == 'falta' else random.choice(sanciones_delito)
    proceso = 'Falta administrativa' if discriminador == 'falta' else 'Delito'

    release_date = entry + timedelta(hours=hrs_cal + random.randint(1, 6)) if (liberado and hrs_cal > 0) else None
    official_release = release_date if liberado else None

    rec, _ = Records.objects.get_or_create(
        folio_afi=folio,
        defaults=dict(
            detainee=det, district=distrito,
            entry_date=entry,
            process=proceso,
            fundament=random.randint(0, 30),
            sanction=sancion,
            has_been_released=liberado,
            qualification_release_date=release_date,
            official_release_date=official_release,
            notes=None, is_active=True
        )
    )

    if not liberado:
        letra = random.choice(['A', 'B', 'C', 'D'])
        num = random.randint(1, 12)
        Cells.objects.get_or_create(
            record=rec, cell=f'{letra}-{num:02d}',
            defaults=dict(
                registered_by=random.choice(agentes_lista).replace('Agente ', ''),
                cell_notes=None,
                registered_belongings=random.choice([True, False]),
                total_belongings=random.randint(0, 6),
                registered_calls=False, total_calls=0
            )
        )

    agente1 = random.choice(agentes_lista)
    agente2 = random.choice(agentes_lista)
    via = random.choice(vias)
    calle = random.choice(apellidos)
    Events.objects.get_or_create(
        record=rec,
        defaults=dict(
            event_datetime=entry - timedelta(hours=random.randint(1, 4)),
            detention_datetime=entry,
            discriminator=discriminador,
            type=tipo_ev,
            subtype=subtipo_ev,
            violence=violencia_ev,
            detention_type=random.choice(['Flagrancia', 'Orden de aprehension', 'Presentacion voluntaria']),
            reason=subtipo_ev,
            arrested_by=agente1,
            place=f'{via} {calle} y {random.choice(apellidos)}',
            unit=random.choice(unidades),
            sector=random.choice(sectores),
            municipality='Juarez',
            country='Mexico',
            colony=random.choice(colonias),
            minimum_salaries=min_sal,
            qualified_hours=hrs_cal,
            qualifies=(discriminador == 'falta'),
            total_payable=float(min_sal * 103.74) if min_sal > 0 else 0.0,
            created_by='Usuario'
        )
    )

    if random.random() > 0.25:
        tiene_lesiones = random.random() > 0.70
        intox_opts = ['Ninguna'] * 5 + ['Alcohol leve', 'Alcohol moderado', 'Marihuana', 'Multiples sustancias']
        mental_opts = ['Lucido'] * 5 + ['Somnoliento', 'Agitado', 'Nervioso', 'Confuso']
        MedicalInformation.objects.get_or_create(
            folio=f'MED-{200+i:03d}',
            defaults=dict(
                record=rec, user=karsam,
                weight=str(random.randint(45, 115)),
                height=f'1.{random.randint(50, 95)}',
                intoxication=random.choice(intox_opts),
                mental=random.choice(mental_opts),
                general_condition=random.choice(['Bueno', 'Bueno', 'Regular', 'Malo']) if tiene_lesiones else random.choice(['Bueno', 'Bueno', 'Regular']),
                medic_name='Dr. Carlos Ramirez',
                medical_cedula='12345678',
                medical_date_time=entry + timedelta(minutes=random.randint(15, 90)),
                pathologies=random.choice(patologias),
                medical_t=f'{random.uniform(36.0, 38.9):.1f}',
                medical_fc=str(random.randint(58, 115)),
                medical_fr=str(random.randint(12, 24)),
                medical_ta=f'{random.randint(100, 145)}/{random.randint(60, 95)}',
                saturation=f'{random.randint(93, 99)}%',
                diagnostic=random.choice(diagnosticos_con_lesion) if tiene_lesiones else random.choice(diagnosticos_sin_lesion),
                blood_type=random.choice(tipos_sangre),
                rh_factor=random.choice(['Positivo', 'Negativo']),
                has_lesions=tiene_lesiones,
                created_by='karsam'
            )
        )

    if (i + 1) % 25 == 0:
        print(f'  {i+1}/100 generados...')

print()
print('=' * 45)
print('RESUMEN FINAL DE LA BASE DE DATOS')
print('=' * 45)
from records.models import Records, Cells, Events, MedicalInformation, Belongings, Actions
total_det = Detainee.objects.count()
total_rec = Records.objects.count()
activos   = Records.objects.filter(has_been_released=False).count()
liberados = Records.objects.filter(has_been_released=True).count()
faltas    = Records.objects.filter(process='Falta administrativa').count()
delitos   = Records.objects.filter(process='Delito').count()
print(f'Detenidos:          {total_det}')
print(f'Expedientes:        {total_rec}')
print(f'  - Activos:        {activos}')
print(f'  - Liberados:      {liberados}')
print(f'  - Faltas:         {faltas}')
print(f'  - Delitos:        {delitos}')
print(f'Celdas:             {Cells.objects.count()}')
print(f'Eventos:            {Events.objects.count()}')
print(f'Registros medicos:  {MedicalInformation.objects.count()}')
print(f'Acciones legales:   {Actions.objects.count()}')
print(f'Pertenencias:       {Belongings.objects.count()}')
print()
print('Distribucion por distrito:')
for d in District.objects.all():
    c = Records.objects.filter(district=d).count()
    print(f'  {d.name}: {c} expedientes')
print()
print('OK Listo. 100 registros nuevos cargados.')
