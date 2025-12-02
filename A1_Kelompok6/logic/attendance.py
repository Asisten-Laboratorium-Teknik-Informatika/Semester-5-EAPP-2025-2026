"""
Modul attendance: clock in/out, laporan, statistik, dsb.
"""

from __future__ import annotations

import csv
import os
from datetime import date, datetime, time, timedelta
from typing import Dict, List, Optional, Tuple

import eel  # type: ignore

from logic.database import get_db_connection
from logic.utils import CURRENT_USER_SESSION

WORK_START_TIME = time(8, 30)
WORK_END_TIME = time(17, 0)
EXPECTED_CLOCK_IN = time(8, 30)


def _to_time(obj) -> Optional[time]:
    if obj is None:
        return None
    if isinstance(obj, time):
        return obj
    if isinstance(obj, datetime):
        return obj.time()
    if isinstance(obj, timedelta):
        total = int(obj.total_seconds())
        hour = (total // 3600) % 24
        minute = (total // 60) % 60
        second = total % 60
        return time(hour, minute, second)
    string = str(obj)
    try:
        if len(string.split(":")) == 2:
            return datetime.strptime(string, "%H:%M").time()
        return datetime.strptime(string.split(".")[0], "%H:%M:%S").time()
    except ValueError:
        return None


def _get_user_column_flags(cursor) -> Dict[str, bool]:
    flags = {"name": False, "department": False}
    try:
        cursor.execute("SHOW COLUMNS FROM users")
        for row in cursor.fetchall():
            field = None
            if isinstance(row, dict):
                field = row.get("Field")
            elif isinstance(row, (list, tuple)) and row:
                field = row[0]
            if field == "name":
                flags["name"] = True
            if field == "department":
                flags["department"] = True
    except Exception:
        pass
    return flags


def calculate_hours(clock_in_time, clock_out_time) -> float:
    if not clock_in_time or not clock_out_time:
        return 0.0
    ci = _to_time(clock_in_time)
    co = _to_time(clock_out_time)
    if not ci or not co:
        return 0.0
    ci_dt = datetime.combine(date.today(), ci)
    co_dt = datetime.combine(date.today(), co)
    if co_dt < ci_dt:
        co_dt += timedelta(days=1)
    diff = co_dt - ci_dt
    return round(diff.total_seconds() / 3600.0, 2)


def check_late(clock_in_time) -> Tuple[bool, int]:
    ci = _to_time(clock_in_time)
    if not ci:
        return False, 0
    if ci > EXPECTED_CLOCK_IN:
        diff = datetime.combine(date.today(), ci) - datetime.combine(date.today(), EXPECTED_CLOCK_IN)
        return True, int(diff.total_seconds() / 60)
    return False, 0


def _resolve_employee_id(employee_id: Optional[str]) -> str:
    if employee_id:
        return employee_id
    if CURRENT_USER_SESSION.get("employee_id"):
        return CURRENT_USER_SESSION["employee_id"]
    return "USER001"


@eel.expose
def clock_in(employee_id=None):
    try:
        employee_id = _resolve_employee_id(employee_id)
        conn = get_db_connection()
        if not conn:
            return {"error": "Tidak dapat terhubung ke database"}
        cur = conn.cursor(dictionary=True, buffered=True)
        today = date.today()

        cur.execute(
            """
            SELECT * FROM attendance
            WHERE employee_id = %s AND date = %s
              AND clock_in IS NOT NULL
              AND (clock_out IS NULL OR clock_out = '')
            ORDER BY id DESC LIMIT 1
            """,
            (employee_id, today),
        )
        open_session = cur.fetchone()
        if open_session:
            cur.close()
            conn.close()
            return {
                "error": f"Anda sudah clock in pada {open_session['clock_in']} dan belum clock out."
            }

        now = datetime.now()
        clock_in_time = now.time()

        is_late, late_minutes = check_late(clock_in_time)
        cur.execute(
            """
            INSERT INTO attendance (employee_id, date, clock_in, is_late, late_minutes)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (employee_id, today, clock_in_time, is_late, late_minutes),
        )
        conn.commit()

        cur.execute(
            """
            SELECT * FROM attendance
            WHERE employee_id = %s AND date = %s
            ORDER BY id DESC LIMIT 1
            """,
            (employee_id, today),
        )
        record = cur.fetchone()
        cur.close()
        conn.close()
        return {
            "success": True,
            "employee_id": employee_id,
            "date": str(today),
            "clock_in": str(clock_in_time),
            "is_late": is_late,
            "late_minutes": late_minutes,
            "expected_clock_in": str(EXPECTED_CLOCK_IN),
        }
    except Exception as exc:
        import traceback

        traceback.print_exc()
        return {"error": f"Error saat clock in: {exc}"}


@eel.expose
def clock_out(employee_id=None):
    try:
        employee_id = _resolve_employee_id(employee_id)
        conn = get_db_connection()
        if not conn:
            return {"error": "Tidak dapat terhubung ke database"}
        cur = conn.cursor(dictionary=True, buffered=True)
        today = date.today()
        cur.execute(
            """
            SELECT * FROM attendance
            WHERE employee_id = %s AND date = %s
              AND clock_in IS NOT NULL
              AND (clock_out IS NULL OR clock_out = '')
            ORDER BY id DESC LIMIT 1
            """,
            (employee_id, today),
        )
        record = cur.fetchone()
        if not record:
            cur.close()
            conn.close()
            return {"error": "Anda belum clock in hari ini"}

        now = datetime.now()
        clock_out_time = now.time()
        total_hours = calculate_hours(record["clock_in"], clock_out_time)
        cur.execute(
            """
            UPDATE attendance
            SET clock_out = %s, total_hours = %s
            WHERE id = %s
            """,
            (clock_out_time, total_hours, record["id"]),
        )
        conn.commit()

        cur.close()
        conn.close()
        return {
            "success": True,
            "employee_id": employee_id,
            "date": str(today),
            "clock_in": str(record["clock_in"]),
            "clock_out": str(clock_out_time),
            "total_hours": total_hours,
        }
    except Exception as exc:
        import traceback

        traceback.print_exc()
        return {"error": f"Error saat clock out: {exc}"}


@eel.expose
def get_current_status(employee_id=None):
    try:
        employee_id = _resolve_employee_id(employee_id)
        conn = get_db_connection()
        if not conn:
            return {"error": "Tidak dapat terhubung ke database"}
        cur = conn.cursor(dictionary=True)
        today = date.today()
        cur.execute(
            """
            SELECT * FROM attendance
            WHERE employee_id = %s AND date = %s
            ORDER BY id DESC LIMIT 1
            """,
            (employee_id, today),
        )
        record = cur.fetchone()

        cur.execute(
            """
            SELECT clock_in, clock_out FROM attendance
            WHERE employee_id = %s AND date = %s
            """,
            (employee_id, today),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()

        total_today = 0.0
        current_session_hours = 0.0
        now_time = datetime.now().time()
        for r in rows:
            if r["clock_in"] and r["clock_out"]:
                total_today += calculate_hours(r["clock_in"], r["clock_out"])
            elif r["clock_in"]:
                hours = calculate_hours(r["clock_in"], now_time)
                total_today += hours
                current_session_hours = hours

        if not record:
            return {
                "is_clocked_in": False,
                "clock_in": None,
                "clock_out": None,
                "total_hours": 0,
                "current_session_hours": 0,
                "today_total_hours": round(total_today, 2),
                "expected_clock_in": str(EXPECTED_CLOCK_IN),
                "is_late": False,
                "late_minutes": 0,
            }

        is_clocked_in = record.get("clock_in") and not record.get("clock_out")
        is_late = bool(record.get("is_late"))
        late_minutes = int(record.get("late_minutes") or 0)

        return {
            "is_clocked_in": bool(is_clocked_in),
            "clock_in": str(record.get("clock_in")) if record.get("clock_in") else None,
            "clock_out": str(record.get("clock_out")) if record.get("clock_out") else None,
            "total_hours": float(record.get("total_hours") or 0),
            "current_session_hours": round(current_session_hours, 2),
            "today_total_hours": round(total_today, 2),
            "expected_clock_in": str(EXPECTED_CLOCK_IN),
            "is_late": is_late,
            "late_minutes": late_minutes,
        }
    except Exception as exc:
        import traceback

        traceback.print_exc()
        return {"error": f"Error getting status: {exc}"}


@eel.expose
def get_today_attendance(employee_id=None):
    try:
        employee_id = _resolve_employee_id(employee_id)
        conn = get_db_connection()
        if not conn:
            return []
        cur = conn.cursor(dictionary=True)
        today = date.today()
        cur.execute(
            """
            SELECT * FROM attendance
            WHERE employee_id = %s AND date = %s
            ORDER BY created_at DESC
            """,
            (employee_id, today),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        result = []
        now_time = datetime.now().time()
        for r in rows:
            hours = float(r.get("total_hours") or 0)
            if r.get("clock_in") and not r.get("clock_out"):
                hours = calculate_hours(r["clock_in"], now_time)
            result.append(
                {
                    "id": r["id"],
                    "employee_id": r["employee_id"],
                    "date": str(r["date"]),
                    "clock_in": str(r["clock_in"]) if r.get("clock_in") else None,
                    "clock_out": str(r["clock_out"]) if r.get("clock_out") else None,
                    "total_hours": round(hours, 2),
                    "is_late": bool(r.get("is_late")),
                    "late_minutes": int(r.get("late_minutes") or 0),
                }
            )
        return result
    except Exception as exc:
        import traceback

        traceback.print_exc()
        return []


@eel.expose
def get_attendance_employees():
    try:
        conn = get_db_connection()
        if not conn:
            return []
        cur = conn.cursor(dictionary=True)
        today = date.today()
        flags = _get_user_column_flags(cur)
        name_expr = "u.name" if flags["name"] else "NULL"
        dept_expr = "u.department" if flags["department"] else "NULL"
        query = f"""
            SELECT a.employee_id,
                   COALESCE({name_expr}, a.employee_id) AS employee_name,
                   COALESCE({dept_expr}, '') AS department,
                   a.clock_in
            FROM attendance a
            LEFT JOIN users u ON u.employee_id = a.employee_id
            WHERE a.date = %s
              AND a.clock_in IS NOT NULL
              AND (a.clock_out IS NULL OR a.clock_out = '')
            ORDER BY a.clock_in
        """
        cur.execute(query, (today,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        result = []
        for r in rows:
            ci = _to_time(r.get("clock_in"))
            result.append(
                {
                    "employee_id": r["employee_id"],
                    "employee_name": r["employee_name"],
                    "department": r.get("department", ""),
                    "status": "Hadir",
                    "clock_in": ci.strftime("%H:%M:%S") if ci else None,
                }
            )
        return result
    except Exception as exc:
        import traceback

        traceback.print_exc()
        return []


def _build_records_for_range(cursor, start_date, end_date, employee_id=None, extra_filter=""):
    flags = _get_user_column_flags(cursor)
    name_expr = "u.name" if flags["name"] else "NULL"
    dept_expr = "u.department" if flags["department"] else "NULL"
    query = f"""
        SELECT a.*,
               COALESCE({name_expr}, a.employee_id) AS employee_name,
               COALESCE({dept_expr}, '') AS department
        FROM attendance a
        LEFT JOIN users u ON u.employee_id = a.employee_id
        WHERE a.date BETWEEN %s AND %s
          AND a.clock_in IS NOT NULL
    """
    params: List = [start_date, end_date]
    if employee_id:
        query += " AND a.employee_id = %s"
        params.append(employee_id)
    if extra_filter:
        query += f" {extra_filter}"
    query += " ORDER BY a.date DESC, a.clock_in DESC"
    cursor.execute(query, params)
    records = cursor.fetchall()
    now_time = datetime.now().time()
    for record in records:
        if record.get("clock_in") and record.get("clock_out"):
            hours = calculate_hours(record["clock_in"], record["clock_out"])
            if abs(hours - float(record.get("total_hours") or 0)) > 0.01:
                record["total_hours"] = hours
        elif record.get("clock_in"):
            record["total_hours"] = calculate_hours(record["clock_in"], now_time)
    return records


@eel.expose
def get_attendance_report(start_date, end_date, employee_id=None):
    try:
        if not start_date or not end_date:
            return {"error": "Tanggal mulai dan tanggal akhir harus diisi"}
        conn = get_db_connection()
        if not conn:
            return {"error": "Tidak dapat terhubung ke database"}
        cur = conn.cursor(dictionary=True)
        records = _build_records_for_range(cur, start_date, end_date, employee_id)
        cur.close()
        conn.close()

        total_records = len(records)
        total_hours = sum(float(r.get("total_hours") or 0) for r in records)
        clock_ins = sum(1 for r in records if r.get("clock_in"))
        clock_outs = sum(1 for r in records if r.get("clock_out"))
        late_count = sum(1 for r in records if r.get("is_late"))
        working_days = len({str(r["date"]) for r in records})
        avg_per_day = total_hours / working_days if working_days else 0

        data = [
            {
                "id": r["id"],
                "employee_id": r["employee_id"],
                "employee_name": r.get("employee_name", r["employee_id"]),
                "department": r.get("department", ""),
                "date": str(r["date"]),
                "clock_in": str(r["clock_in"]) if r.get("clock_in") else None,
                "clock_out": str(r["clock_out"]) if r.get("clock_out") else None,
                "total_hours": float(r.get("total_hours") or 0),
                "is_late": bool(r.get("is_late")),
                "late_minutes": int(r.get("late_minutes") or 0),
            }
            for r in records
        ]

        return {
            "success": True,
            "period": {"start_date": start_date, "end_date": end_date},
            "data": data,
            "statistics": {
                "total_records": total_records,
                "working_days": working_days,
                "total_hours": round(total_hours, 2),
                "average_hours_per_day": round(avg_per_day, 2),
                "clock_ins": clock_ins,
                "clock_outs": clock_outs,
                "late_count": late_count,
                "on_time_count": clock_ins - late_count,
            },
        }
    except Exception as exc:
        import traceback

        traceback.print_exc()
        return {"error": f"Error getting report: {exc}"}


@eel.expose
def get_attendance_statistics(employee_id=None, days=30):
    try:
        employee_id = _resolve_employee_id(employee_id)
        if not days or days < 1:
            days = 30
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)
        conn = get_db_connection()
        if not conn:
            return {"error": "Tidak dapat terhubung ke database"}
        cur = conn.cursor(dictionary=True)
        records = _build_records_for_range(cur, start_date, end_date, employee_id)
        cur.close()
        conn.close()

        total_records = len(records)
        total_hours = sum(float(r.get("total_hours") or 0) for r in records)
        clock_ins = sum(1 for r in records if r.get("clock_in"))
        clock_outs = sum(1 for r in records if r.get("clock_out"))
        late_count = sum(1 for r in records if r.get("is_late"))
        working_days = len({str(r["date"]) for r in records})
        avg_hours_per_day = total_hours / working_days if working_days else 0
        avg_hours_per_workday = total_hours / clock_ins if clock_ins else 0
        weeks = days / 7.0
        avg_weekly_hours = total_hours / weeks if weeks else 0
        attendance_rate = (clock_ins / days * 100) if days else 0
        hours_list = [float(r.get("total_hours") or 0) for r in records]
        max_hours = max(hours_list) if hours_list else 0
        min_hours = min(hours_list) if hours_list else 0

        weekly_breakdown: Dict[str, float] = {}
        for r in records:
            record_date = r["date"]
            if isinstance(record_date, str):
                record_date = datetime.strptime(record_date, "%Y-%m-%d").date()
            week_start = record_date - timedelta(days=record_date.weekday())
            key = week_start.strftime("%Y-%m-%d")
            weekly_breakdown.setdefault(key, 0.0)
            weekly_breakdown[key] += float(r.get("total_hours") or 0)

        return {
            "success": True,
            "period_days": days,
            "statistics": {
                "total_records": total_records,
                "working_days": working_days,
                "total_hours": round(total_hours, 2),
                "average_hours_per_day": round(avg_hours_per_day, 2),
                "average_hours_per_working_day": round(avg_hours_per_workday, 2),
                "average_weekly_hours": round(avg_weekly_hours, 2),
                "attendance_rate": round(attendance_rate, 2),
                "clock_ins": clock_ins,
                "clock_outs": clock_outs,
                "late_count": late_count,
                "on_time_count": clock_ins - late_count,
                "max_hours": round(max_hours, 2),
                "min_hours": round(min_hours, 2),
            },
            "weekly_breakdown": weekly_breakdown,
        }
    except Exception as exc:
        import traceback

        traceback.print_exc()
        return {"error": f"Error getting statistics: {exc}"}


@eel.expose
def check_late_arrival(employee_id=None, check_date=None):
    try:
        employee_id = _resolve_employee_id(employee_id)
        if not check_date:
            check_date = date.today()
        else:
            check_date = datetime.strptime(check_date, "%Y-%m-%d").date()

        conn = get_db_connection()
        if not conn:
            return {"error": "Tidak dapat terhubung ke database"}
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT * FROM attendance
            WHERE employee_id = %s AND date = %s
            ORDER BY id DESC LIMIT 1
            """,
            (employee_id, check_date),
        )
        record = cur.fetchone()
        cur.close()
        conn.close()
        if not record or not record.get("clock_in"):
            return {"error": f"Tidak ada data clock in untuk tanggal {check_date}"}
        clock_in_time = _to_time(record["clock_in"])
        is_late, late_minutes = check_late(clock_in_time)
        expected_dt = datetime.combine(check_date, EXPECTED_CLOCK_IN)
        actual_dt = datetime.combine(check_date, clock_in_time)
        diff_minutes = int((actual_dt - expected_dt).total_seconds() / 60)
        return {
            "is_late": is_late,
            "expected_time": str(EXPECTED_CLOCK_IN),
            "actual_time": str(clock_in_time),
            "difference_minutes": abs(diff_minutes),
            "difference_hours": round(abs(diff_minutes) / 60, 2),
            "message": f"{'Terlambat' if is_late else 'Tepat waktu'} {abs(diff_minutes)} menit",
        }
    except Exception as exc:
        import traceback

        traceback.print_exc()
        return {"error": f"Error checking late arrival: {exc}"}


@eel.expose
def search_attendance_records(
    start_date=None,
    end_date=None,
    employee_id=None,
    employee_name=None,
    department=None,
    min_hours=None,
    max_hours=None,
    late_only=False,
):
    try:
        conn = get_db_connection()
        if not conn:
            return {"error": "Tidak dapat terhubung ke database"}
        cur = conn.cursor(dictionary=True)
        flags = _get_user_column_flags(cur)
        name_expr = "u.name" if flags["name"] else "NULL"
        dept_expr = "u.department" if flags["department"] else "NULL"

        query = f"""
            SELECT a.*,
                   COALESCE({name_expr}, a.employee_id) AS employee_name,
                   COALESCE({dept_expr}, '') AS department
            FROM attendance a
            LEFT JOIN users u ON u.employee_id = a.employee_id
            WHERE a.clock_in IS NOT NULL
        """
        params: List = []
        if start_date:
            query += " AND a.date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND a.date <= %s"
            params.append(end_date)
        if employee_id:
            query += " AND a.employee_id = %s"
            params.append(employee_id)
        if employee_name:
            if flags["name"]:
                query += " AND (u.name LIKE %s OR a.employee_id LIKE %s)"
                params.extend([f"%{employee_name}%", f"%{employee_name}%"])
            else:
                query += " AND a.employee_id LIKE %s"
                params.append(f"%{employee_name}%")
        if department and flags["department"]:
            query += " AND u.department LIKE %s"
            params.append(f"%{department}%")
        if late_only:
            query += " AND a.is_late = TRUE"
        query += " ORDER BY a.date DESC, a.clock_in DESC"
        cur.execute(query, params)
        records = cur.fetchall()
        cur.close()
        conn.close()

        now_time = datetime.now().time()
        filtered = []
        for r in records:
            total_hours = float(r.get("total_hours") or 0)
            if r.get("clock_in") and not r.get("clock_out"):
                total_hours = calculate_hours(r["clock_in"], now_time)
            if min_hours is not None and total_hours < float(min_hours):
                continue
            if max_hours is not None and total_hours > float(max_hours):
                continue
            filtered.append(
                {
                    "id": r["id"],
                    "employee_id": r["employee_id"],
                    "employee_name": r.get("employee_name", r["employee_id"]),
                    "department": r.get("department", ""),
                    "date": str(r["date"]),
                    "clock_in": str(r["clock_in"]) if r.get("clock_in") else None,
                    "clock_out": str(r["clock_out"]) if r.get("clock_out") else None,
                    "total_hours": round(total_hours, 2),
                    "is_late": bool(r.get("is_late")),
                    "late_minutes": int(r.get("late_minutes") or 0),
                }
            )
        return {"total_records": len(filtered), "records": filtered}
    except Exception as exc:
        import traceback

        traceback.print_exc()
        return {"error": f"Error searching records: {exc}"}


@eel.expose
def get_recent_activity(employee_id=None, limit=10):
    try:
        employee_id = _resolve_employee_id(employee_id)
        if not limit or limit < 1:
            limit = 10
        conn = get_db_connection()
        if not conn:
            return []
        cur = conn.cursor(dictionary=True)
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        cur.execute(
            """
            SELECT * FROM attendance
            WHERE employee_id = %s
              AND date BETWEEN %s AND %s
              AND (clock_in IS NOT NULL OR clock_out IS NOT NULL)
            ORDER BY date DESC,
                     CASE
                        WHEN clock_out IS NOT NULL THEN clock_out
                        WHEN clock_in IS NOT NULL THEN clock_in
                        ELSE '00:00:00'
                     END DESC
            LIMIT %s
            """,
            (employee_id, start_date, end_date, limit),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        activities = []
        for r in rows:
            record_date = r["date"]
            if isinstance(record_date, str):
                record_date = datetime.strptime(record_date, "%Y-%m-%d").date()
            if record_date == date.today():
                display = "Hari ini"
            elif record_date == date.today() - timedelta(days=1):
                display = "Kemarin"
            else:
                display = record_date.strftime("%d %b %Y")
            if r.get("clock_in"):
                ci_time = _to_time(r["clock_in"])
                activities.append(
                    {
                        "type": "clock_in",
                        "title": f"Clock In{' (Terlambat)' if r.get('is_late') else ''}",
                        "time": ci_time.strftime("%H:%M") if ci_time else "",
                        "date": str(record_date),
                        "date_display": display,
                        "is_late": bool(r.get("is_late")),
                        "timestamp": datetime.combine(record_date, ci_time).timestamp()
                        if ci_time
                        else 0,
                    }
                )
            if r.get("clock_out"):
                co_time = _to_time(r["clock_out"])
                activities.append(
                    {
                        "type": "clock_out",
                        "title": f"Clock Out ({float(r.get('total_hours') or 0):.1f} jam)",
                        "time": co_time.strftime("%H:%M") if co_time else "",
                        "date": str(record_date),
                        "date_display": display,
                        "total_hours": float(r.get("total_hours") or 0),
                        "timestamp": datetime.combine(record_date, co_time).timestamp()
                        if co_time
                        else 0,
                    }
                )
        activities.sort(key=lambda item: item["timestamp"], reverse=True)
        return activities[:limit]
    except Exception as exc:
        import traceback

        traceback.print_exc()
        return []


@eel.expose
def export_attendance_to_csv(start_date=None, end_date=None, employee_id=None):
    try:
        if not start_date:
            start_date = "2020-01-01"
        if not end_date:
            end_date = str(date.today())
        report = get_attendance_report(start_date, end_date, employee_id)
        if report.get("error"):
            return {"error": report["error"]}
        if not report.get("success"):
            return {"error": "Tidak ada data untuk diekspor"}
        data = report.get("data") or []
        if not data:
            return {"error": "Tidak ada data untuk diekspor"}

        export_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")
        os.makedirs(export_dir, exist_ok=True)
        filename = f"attendance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(export_dir, filename)
        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "Tanggal",
                "Employee ID",
                "Nama",
                "Departemen",
                "Clock In",
                "Clock Out",
                "Total Jam",
                "Terlambat",
                "Menit Terlambat",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for record in data:
                writer.writerow(
                    {
                        "Tanggal": record.get("date", ""),
                        "Employee ID": record.get("employee_id", ""),
                        "Nama": record.get("employee_name", ""),
                        "Departemen": record.get("department", ""),
                        "Clock In": record.get("clock_in", ""),
                        "Clock Out": record.get("clock_out", ""),
                        "Total Jam": record.get("total_hours", 0),
                        "Terlambat": "Ya" if record.get("is_late") else "Tidak",
                        "Menit Terlambat": record.get("late_minutes", 0),
                    }
                )
        return {
            "success": True,
            "message": f"Data berhasil diekspor ke {filename}",
            "filename": filename,
            "filepath": filepath,
            "records_exported": len(data),
        }
    except Exception as exc:
        import traceback

        traceback.print_exc()
        return {"error": f"Error exporting to CSV: {exc}"}

