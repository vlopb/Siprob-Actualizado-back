"""
Fix all dropdown mismatches between DB values and Angular dropdown values.
Also assign default photo to all detainees.
"""
import os, shutil
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from detainees.models import Detainee, Photos
from records.models import MedicalInformation
from django.conf import settings

# ─── 1. DETAINEE FIELD MAPPINGS ───────────────────────────────────────────────

NATIONALITY_MAP = {
    'Mexicana': 'MEX', 'Americana': 'USA', 'Estadounidense': 'USA',
    'Guatemalteca': 'GTM', 'Hondureña': 'HND', 'Salvadoreña': 'SLV',
    'Cubana': 'CUB', 'Colombiana': 'COL', 'Venezolana': 'VEN',
}

SCHOOLING_MAP = {
    'Sin estudios': 'sin escolaridad',
    'Tecnico': 'educación técnica',
    'Universidad': 'licenciatura',
    'Preparatoria': 'preparatoria',
    'Primaria': 'primaria',
    'Secundaria': 'secundaria',
    'Preescolar': 'preescolar',
    'Maestría': 'maestría',
    'Doctorado': 'doctorado',
}

MARITAL_MAP = {
    'Soltero': 'soltero/a', 'Soltera': 'soltero/a',
    'Casado': 'casado/a', 'Casada': 'casado/a',
    'Divorciado': 'divorciado/a', 'Divorciada': 'divorciado/a',
    'Viudo': 'viudo/a', 'Viuda': 'viudo/a',
    'Unión libre': 'unión libre', 'Union libre': 'unión libre',
}

GENDER_MAP = {
    'Masculino': 'male', 'Hombre': 'male', 'M': 'male',
    'Femenino': 'female', 'Mujer': 'female', 'F': 'female',
}

SEXUAL_PREF_MAP = {
    'Heterosexual': 'heterosexual', 'Homosexual': 'homosexual',
    'Bisexual': 'bisexual', 'No especifica': 'prefiero no decirlo',
    'Prefiero no decirlo': 'prefiero no decirlo',
}

OCCUPATION_MAP = {
    'Agricultor': 'agricultor',
    'Albanil': 'albañil',
    'Ama de casa': 'ama de casa',
    'Asistente': 'auxiliar',
    'Carpintero': 'carpintero/a',
    'Chofer': 'chofer',
    'Chofer privado': 'chofer privado',
    'Chofer público': 'chofer público',
    'Cocinera': 'cocinero/a',
    'Cocinero': 'cocinero/a',
    'Comerciante': 'comerciante',
    'Costurera': 'costurero/a',
    'Costurero': 'costurero/a',
    'Desempleada': 'desempleada/o',
    'Desempleado': 'desempleada/o',
    'Electricista': 'electricista',
    'Empleada': 'empleado/a',
    'Empleado': 'empleado/a',
    'Enfermera': 'enfermero/a',
    'Enfermero': 'enfermero/a',
    'Estilista': 'estilista',
    'Estudiante': 'estudiante',
    'Jardinero': 'jardinero/a',
    'Jardinera': 'jardinero/a',
    'Maestra': 'maestro/a',
    'Maestro': 'maestro/a',
    'Mecanico': 'mecánico',
    'Mecánico': 'mecánico',
    'Mesera': 'camarero/a',
    'Mesero': 'camarero/a',
    'Obrera': 'obrera',
    'Obrero': 'obrera',
    'Plomero': 'plomero/a',
    'Repartidor': 'repartidor',
    'Secretaria': 'secretario/a',
    'Secretario': 'secretario/a',
    'Seguridad': 'guardia',
    'Guardia': 'guardia',
    'Vendedor': 'vendedor',
    'Vendedora': 'vendedor',
    'Ingeniero': 'ingeniero/a',
    'Ingeniería': 'ingeniero/a',
    'Médico': 'médico',
    'Policia': 'policía',
    'Taxista': 'taxista',
    'Contador': 'contador',
}

# ─── 2. MEDICAL FIELD MAPPINGS ────────────────────────────────────────────────

INTOXICATION_MAP = {
    'No': 'sin datos de intoxicación',
    'Ninguna': 'sin datos de intoxicación',
    'Alcohol': 'aliento alcohólico',
    'Alcohol leve': 'ebriedad primer grado',
    'Alcohol moderado': 'ebriedad segundo grado',
    'Drogas': 'varios',
    'Marihuana': 'probable consumo de marihuana',
    'Cocaína': 'probable consumo de cocaína y derivados',
    'Alcohol y drogas': 'varios',
    'Multiples sustancias': 'varios',
    'Múltiples sustancias': 'varios',
}

MENTAL_MAP = {
    'Lucido': 'normal', 'Lúcido': 'normal', 'Orientado': 'normal', 'Tranquilo': 'normal',
    'Nervioso': 'trastornado', 'Desorientado': 'trastornado',
    'Confuso': 'trastornado', 'Agitado': 'trastornado',
    'Somnoliento': 'alcohólico', 'Ebrio': 'alcohólico',
    'Drogado': 'drogadicto',
}

CONDITION_MAP = {
    'Bueno': 'ileso',
    'Regular': 'ileso',
    'Malo': 'lesión leve',
    'Ileso': 'ileso',
    'Lesionado': 'lesión leve',
    'Grave': 'lesión grave',
}

BLOOD_MAP = {
    'A+': 'A', 'A-': 'A',
    'B+': 'B', 'B-': 'B',
    'O+': 'O', 'O-': 'O',
    'AB+': 'AB', 'AB-': 'AB',
}

RH_MAP = {
    'Positivo': 'positivo', 'positivo': 'positivo',
    'Negativo': 'negativo', 'negativo': 'negativo',
}

# ─── 3. FIX DETAINEES ─────────────────────────────────────────────────────────

print("Fixing Detainee field values...")
detainees = Detainee.objects.all()
fixed = 0
for d in detainees:
    changed = False

    nat = NATIONALITY_MAP.get(d.nationality)
    if nat and d.nationality != nat:
        d.nationality = nat; changed = True

    sch = SCHOOLING_MAP.get(d.schooling)
    if sch and d.schooling != sch:
        d.schooling = sch; changed = True

    mar = MARITAL_MAP.get(d.marital_status)
    if mar and d.marital_status != mar:
        d.marital_status = mar; changed = True

    gen = GENDER_MAP.get(d.gender)
    if gen and d.gender != gen:
        d.gender = gen; changed = True

    sex = SEXUAL_PREF_MAP.get(d.sexual_preferences)
    if sex and d.sexual_preferences != sex:
        d.sexual_preferences = sex; changed = True

    occ = OCCUPATION_MAP.get(d.occupation)
    if occ and d.occupation != occ:
        d.occupation = occ; changed = True

    if changed:
        d.save()
        fixed += 1

print(f"  Fixed {fixed}/{detainees.count()} detainees.")

# ─── 4. FIX MEDICAL INFORMATION ───────────────────────────────────────────────

print("\nFixing MedicalInformation field values...")
med_fixed = 0
for m in MedicalInformation.objects.all():
    changed = False

    intox = INTOXICATION_MAP.get(m.intoxication)
    if intox and m.intoxication != intox:
        m.intoxication = intox; changed = True

    mental = MENTAL_MAP.get(m.mental)
    if mental and m.mental != mental:
        m.mental = mental; changed = True

    cond = CONDITION_MAP.get(m.general_condition)
    if cond and m.general_condition != cond:
        m.general_condition = cond; changed = True

    blood = BLOOD_MAP.get(m.blood_type)
    if blood and m.blood_type != blood:
        m.blood_type = blood; changed = True

    rh = RH_MAP.get(m.rh_factor)
    if rh and m.rh_factor != rh:
        m.rh_factor = rh; changed = True

    if changed:
        m.save()
        med_fixed += 1

print(f"  Fixed {med_fixed}/{MedicalInformation.objects.count()} medical records.")

# ─── 5. ASSIGN DEFAULT PHOTO ──────────────────────────────────────────────────

print("\nAssigning default photo to all detainees...")
photo_dest_dir = os.path.join(settings.MEDIA_ROOT, 'images')
os.makedirs(photo_dest_dir, exist_ok=True)

default_photo_src = '/usr/src/app/150.png'
default_photo_name = 'default_profile.png'
default_photo_dest = os.path.join(photo_dest_dir, default_photo_name)
default_photo_url = f'images/{default_photo_name}'

if os.path.exists(default_photo_src):
    shutil.copy2(default_photo_src, default_photo_dest)
    print(f"  Copied 150.png to {default_photo_dest}")

    photo_created = 0
    for d in Detainee.objects.all():
        photo, created = Photos.objects.update_or_create(
            detainee=d,
            defaults={'image_path': default_photo_url, 'is_active': True}
        )
        if created:
            photo_created += 1

    print(f"  Created/updated photos for {Detainee.objects.count()} detainees ({photo_created} new).")
else:
    print(f"  WARNING: {default_photo_src} not found. Copy 150.png to container first.")

print("\nDone!")
