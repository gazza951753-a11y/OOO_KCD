"""
Seed-скрипт: создаёт суперадмина и тестовые данные при первом запуске.
Запускается через: python -m app.seed
"""
import sys
from datetime import date, time

from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import hash_password
from app.database import SessionLocal
from app.models.document import DocumentRequest, DocumentStatus, DocumentType
from app.models.timekeeping import TimesheetRecord, TimesheetStatus
from app.models.user import Department, User, UserRole


def seed(db: Session) -> None:
    # Skip if superadmin already exists
    if db.query(User).filter(User.role == UserRole.superadmin).first():
        print("Seed: суперадмин уже существует, пропуск.")
        return

    print("Seed: создание начальных данных...")

    # Departments
    dept_it = Department(name="ИТ-отдел")
    dept_hr = Department(name="Отдел кадров")
    db.add_all([dept_it, dept_hr])
    db.flush()

    # Users
    admin = User(
        email=settings.FIRST_SUPERADMIN_EMAIL,
        hashed_password=hash_password(settings.FIRST_SUPERADMIN_PASSWORD),
        full_name="Администратор системы",
        role=UserRole.superadmin,
    )
    hr_user = User(
        email="hr@kcd.ru",
        hashed_password=hash_password("Hr123456!"),
        full_name="Иванова Мария Петровна",
        role=UserRole.hr,
        department_id=dept_hr.id,
        position="Специалист по кадрам",
    )
    manager = User(
        email="manager@kcd.ru",
        hashed_password=hash_password("Manager123!"),
        full_name="Петров Алексей Сергеевич",
        role=UserRole.manager,
        department_id=dept_it.id,
        position="Руководитель ИТ-отдела",
    )
    employee = User(
        email="employee@kcd.ru",
        hashed_password=hash_password("Employee123!"),
        full_name="Сидоров Иван Николаевич",
        role=UserRole.employee,
        department_id=dept_it.id,
        position="Программист",
    )
    db.add_all([admin, hr_user, manager, employee])
    db.flush()

    # Set department managers
    dept_it.manager_id = manager.id
    dept_hr.manager_id = hr_user.id

    # Timesheet records for current month
    today = date.today()
    for day in range(1, min(today.day + 1, 6)):
        rec_date = date(today.year, today.month, day)
        db.add(TimesheetRecord(
            user_id=employee.id,
            date=rec_date,
            check_in=time(9, 0),
            check_out=time(18, 0),
            status=TimesheetStatus.present,
            work_hours=9.0,
        ))
    db.add(TimesheetRecord(
        user_id=employee.id,
        date=date(today.year, today.month, 1),
        check_in=time(9, 0),
        check_out=time(18, 0),
        status=TimesheetStatus.present,
        work_hours=9.0,
        approved_by=manager.id,
    ))

    # Sample document request
    db.add(DocumentRequest(
        requester_id=employee.id,
        type=DocumentType.vacation_request,
        title="Заявление на отпуск",
        description="Прошу предоставить ежегодный оплачиваемый отпуск с 01.04.2026 по 14.04.2026",
        status=DocumentStatus.pending,
    ))

    db.commit()
    print("Seed: данные успешно созданы.")
    print(f"  Суперадмин: {settings.FIRST_SUPERADMIN_EMAIL} / {settings.FIRST_SUPERADMIN_PASSWORD}")
    print("  HR: hr@kcd.ru / Hr123456!")
    print("  Руководитель: manager@kcd.ru / Manager123!")
    print("  Сотрудник: employee@kcd.ru / Employee123!")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed(db)
    except Exception as e:
        print(f"Seed ошибка: {e}", file=sys.stderr)
        db.rollback()
        sys.exit(1)
    finally:
        db.close()
