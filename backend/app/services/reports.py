import io
from datetime import date

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.orm import Session

from app.models.timekeeping import TimesheetRecord
from app.models.user import User

STATUS_LABELS = {
    "present": "Присутствие",
    "absent": "Отсутствие",
    "vacation": "Отпуск",
    "sick": "Больничный",
    "holiday": "Праздник",
    "business_trip": "Командировка",
}


def generate_timesheet_excel(
    db: Session,
    year: int,
    month: int,
    department_id: int | None = None,
    user_id: int | None = None,
) -> bytes:
    query = db.query(TimesheetRecord).join(User, TimesheetRecord.user_id == User.id)
    if department_id:
        query = query.filter(User.department_id == department_id)
    if user_id:
        query = query.filter(TimesheetRecord.user_id == user_id)
    query = query.filter(
        TimesheetRecord.date >= date(year, month, 1),
    )
    from calendar import monthrange
    query = query.filter(
        TimesheetRecord.date <= date(year, month, monthrange(year, month)[1])
    )
    records = query.order_by(TimesheetRecord.date).all()

    wb = Workbook()
    ws = wb.active
    ws.title = f"Табель {month:02d}.{year}"

    # Header style
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill("solid", fgColor="2563EB")
    center = Alignment(horizontal="center")

    headers = ["ФИО", "Дата", "Приход", "Уход", "Статус", "Часов", "Комментарий"]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center

    for row_idx, rec in enumerate(records, 2):
        user = rec.user
        ws.cell(row=row_idx, column=1, value=user.full_name if user else "—")
        ws.cell(row=row_idx, column=2, value=str(rec.date))
        ws.cell(row=row_idx, column=3, value=str(rec.check_in) if rec.check_in else "")
        ws.cell(row=row_idx, column=4, value=str(rec.check_out) if rec.check_out else "")
        ws.cell(row=row_idx, column=5, value=STATUS_LABELS.get(rec.status, rec.status))
        ws.cell(row=row_idx, column=6, value=rec.work_hours or "")
        ws.cell(row=row_idx, column=7, value=rec.comment or "")

    for col in ws.columns:
        max_len = max(len(str(cell.value or "")) for cell in col)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 40)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def generate_timesheet_pdf(
    db: Session,
    year: int,
    month: int,
    department_id: int | None = None,
    user_id: int | None = None,
) -> bytes:
    query = db.query(TimesheetRecord).join(User, TimesheetRecord.user_id == User.id)
    if department_id:
        query = query.filter(User.department_id == department_id)
    if user_id:
        query = query.filter(TimesheetRecord.user_id == user_id)
    from calendar import monthrange
    query = query.filter(
        TimesheetRecord.date >= date(year, month, 1),
        TimesheetRecord.date <= date(year, month, monthrange(year, month)[1]),
    )
    records = query.order_by(TimesheetRecord.date).all()

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=1 * cm, rightMargin=1 * cm)
    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph(f"<b>Табель учёта рабочего времени — {month:02d}/{year}</b>", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 0.5 * cm))

    table_data = [["ФИО", "Дата", "Приход", "Уход", "Статус", "Часов"]]
    for rec in records:
        user = rec.user
        table_data.append([
            user.full_name if user else "—",
            str(rec.date),
            str(rec.check_in) if rec.check_in else "",
            str(rec.check_out) if rec.check_out else "",
            STATUS_LABELS.get(rec.status, rec.status),
            str(rec.work_hours or ""),
        ])

    t = Table(table_data, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563EB")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EFF6FF")]),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(t)

    doc.build(elements)
    return buf.getvalue()
