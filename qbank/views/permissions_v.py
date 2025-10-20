# qbank/permissions.py
from django.core.exceptions import ObjectDoesNotExist

def can_manage_course_questions(user, course, exam) -> bool:
    """
    Kursun soru seçimini yönetebilir mi?
    Kurallar:
      - superuser
      - dersin öğretim elemanı (veya ek-öğretim elemanları, varsa)
      - ilgili sınavın bağlı olduğu CommitteeDepot'un başkanı
    """
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True

    try:
        fct = user.facultyprofile
    except ObjectDoesNotExist:
        return False

    # 1) Dersin öğretim elemanı
    if getattr(course, "lecturer_id", None) == getattr(fct, "id", None):
        return True

    # 1b) Eğer ek-öğretim elemanları M2M/ara modelle tutuluyorsa burada kontrol edin
    # Örn: course.additional_lecturers.filter(pk=fct.id).exists()

    # 2) Bu sınavın bağlı olduğu Committee başkanı
    cmt = getattr(exam, "committee", None)
    if cmt and getattr(cmt, "chair_id", None) == getattr(fct, "id", None):
        return True

    return False
