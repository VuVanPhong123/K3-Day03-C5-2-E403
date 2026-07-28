"""
Tool registry and pure functions for the Recruitment Assistant ReAct Agent.

Tools never import mock data directly. app.py injects the data stores so tests
can run with isolated in-memory copies.
"""

import json
from datetime import datetime


def _dump(payload: dict, indent: int | None = None) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=indent)


def get_candidate_profile(candidate_id: str, candidates_db: dict) -> str:
    """Return one candidate profile by candidate id."""
    try:
        if candidate_id not in candidates_db:
            return _dump({"error": True, "code": "CANDIDATE_NOT_FOUND", "message": f"Không tìm thấy hồ sơ '{candidate_id}'."})
        return _dump({"error": False, "candidate_id": candidate_id, "data": candidates_db[candidate_id]}, indent=2)
    except Exception as exc:
        return _dump({"error": True, "code": "TOOL_EXCEPTION", "message": str(exc)})


def get_job_requirements(job_id: str, jobs_db: dict) -> str:
    """Return one job description by job id."""
    try:
        if job_id not in jobs_db:
            return _dump({"error": True, "code": "JOB_NOT_FOUND", "message": f"Không tìm thấy công việc '{job_id}'."})
        return _dump({"error": False, "job_id": job_id, "data": jobs_db[job_id]}, indent=2)
    except Exception as exc:
        return _dump({"error": True, "code": "TOOL_EXCEPTION", "message": str(exc)})


def evaluate_fit(candidate_id: str, job_id: str, candidates_db: dict, jobs_db: dict) -> str:
    """
    Compare candidate evidence against a job description.

    The output is intentionally neutral: it reports evidence and screening signal,
    not a final hiring decision.
    """
    try:
        if candidate_id not in candidates_db:
            return _dump({"error": True, "code": "CANDIDATE_NOT_FOUND", "message": f"Ứng viên '{candidate_id}' không tồn tại."})
        if job_id not in jobs_db:
            return _dump({"error": True, "code": "JOB_NOT_FOUND", "message": f"Công việc '{job_id}' không tồn tại."})

        candidate = candidates_db[candidate_id]
        job = jobs_db[job_id]
        candidate_skills = {skill.lower() for skill in candidate.get("skills", [])}
        required_skills = {skill.lower() for skill in job.get("required_skills", [])}

        matched = sorted(candidate_skills & required_skills)
        missing = sorted(required_skills - candidate_skills)
        skill_score = len(matched) / len(required_skills) * 100 if required_skills else 0
        required_exp = job.get("experience_min", 0)
        candidate_exp = candidate.get("experience_years", 0)
        experience_score = min(100, (candidate_exp / required_exp) * 100) if required_exp > 0 else 100
        fit_percentage = int((skill_score + experience_score) / 2)

        if fit_percentage >= 85:
            evidence_level = "high_evidence_match"
            next_step = "Có đủ bằng chứng để cân nhắc mời phỏng vấn, nếu HR đồng ý."
        elif fit_percentage >= 70:
            evidence_level = "moderate_evidence_match"
            next_step = "Nên làm rõ các kỹ năng còn thiếu trước khi quyết định bước tiếp theo."
        elif fit_percentage >= 50:
            evidence_level = "partial_evidence_match"
            next_step = "Cần kiểm tra thêm dự án/kinh nghiệm liên quan trước khi mời phỏng vấn."
        else:
            evidence_level = "low_evidence_match"
            next_step = "Chưa đủ bằng chứng phù hợp với JD hiện tại; nên bổ sung dữ liệu hoặc cân nhắc vị trí khác."

        return _dump(
            {
                "error": False,
                "candidate_id": candidate_id,
                "job_id": job_id,
                "fit_percentage": fit_percentage,
                "evidence_level": evidence_level,
                "matched_skills": matched,
                "missing_skills": missing,
                "skill_score": round(skill_score, 1),
                "experience_score": round(experience_score, 1),
                "candidate_experience": candidate_exp,
                "job_required_experience": required_exp,
                "next_step_note": next_step,
                "decision_boundary": "Tool chỉ cung cấp tín hiệu sàng lọc; quyết định tuyển dụng cuối cùng thuộc về con người.",
            },
            indent=2,
        )
    except Exception as exc:
        return _dump({"error": True, "code": "TOOL_EXCEPTION", "message": str(exc)})


def check_interview_schedule(date: str, interview_schedule: dict, booked_interviews: dict) -> str:
    """Check available interview slots for a date."""
    try:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return _dump(
                {
                    "error": True,
                    "code": "INVALID_DATE",
                    "message": f"Ngày '{date}' không hợp lệ. Dùng định dạng YYYY-MM-DD.",
                }
            )

        today = datetime.now().strftime("%Y-%m-%d")
        if date < today:
            return _dump(
                {
                    "error": True,
                    "code": "PAST_DATE",
                    "message": f"Không thể đặt lịch trong quá khứ. Ngày yêu cầu: {date}; hôm nay: {today}.",
                }
            )

        if date not in interview_schedule:
            return _dump(
                {
                    "error": True,
                    "code": "DATE_NOT_AVAILABLE",
                    "message": f"Không có lịch phỏng vấn cho ngày {date}.",
                    "available_dates": sorted(interview_schedule.keys()),
                }
            )

        booked_slots = [booking["time"] for booking in booked_interviews.values() if booking["date"] == date]
        available_slots = [slot for slot in interview_schedule[date] if slot not in booked_slots]
        return _dump(
            {
                "error": False,
                "date": date,
                "available_slots": available_slots,
                "booked_slots": booked_slots,
                "total_slots": len(interview_schedule[date]),
                "available_count": len(available_slots),
            },
            indent=2,
        )
    except Exception as exc:
        return _dump({"error": True, "code": "TOOL_EXCEPTION", "message": str(exc)})


def schedule_interview(
    candidate_id: str,
    date: str,
    time: str,
    job_id: str,
    confirmed: bool,
    candidates_db: dict,
    interview_schedule: dict,
    booked_interviews: dict,
) -> str:
    """Create an in-memory interview booking only after explicit confirmation."""
    try:
        if confirmed is not True:
            return _dump(
                {
                    "error": True,
                    "code": "NEED_CONFIRMATION",
                    "message": "Cần xác nhận rõ ràng trước khi đặt lịch. Không có thay đổi nào được ghi.",
                }
            )

        if candidate_id not in candidates_db:
            return _dump({"error": True, "code": "CANDIDATE_NOT_FOUND", "message": f"Ứng viên '{candidate_id}' không tồn tại."})

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return _dump({"error": True, "code": "INVALID_DATE", "message": f"Ngày '{date}' không hợp lệ. Dùng YYYY-MM-DD."})

        try:
            datetime.strptime(time, "%H:%M")
        except ValueError:
            return _dump({"error": True, "code": "INVALID_TIME", "message": f"Giờ '{time}' không hợp lệ. Dùng HH:MM."})

        if date not in interview_schedule:
            return _dump(
                {
                    "error": True,
                    "code": "DATE_NOT_AVAILABLE",
                    "message": f"Không có lịch cho ngày {date}.",
                    "available_dates": sorted(interview_schedule.keys()),
                }
            )

        if time not in interview_schedule[date]:
            return _dump(
                {
                    "error": True,
                    "code": "TIME_NOT_AVAILABLE",
                    "message": f"Giờ {time} không có trong lịch ngày {date}.",
                    "available_slots": interview_schedule[date],
                }
            )

        for booking in booked_interviews.values():
            if booking["date"] == date and booking["time"] == time:
                return _dump(
                    {
                        "error": True,
                        "code": "SLOT_ALREADY_BOOKED",
                        "message": f"Slot {time} ngày {date} đã bị đặt bởi {booking['candidate_id']}.",
                    }
                )

        interview_id = f"INT_{len(booked_interviews) + 1:03d}"
        candidate = candidates_db[candidate_id]
        booked_interviews[interview_id] = {
            "candidate_id": candidate_id,
            "candidate_name": candidate["name"],
            "candidate_email": candidate["email"],
            "date": date,
            "time": time,
            "job_id": job_id,
            "status": "confirmed",
            "booked_at": datetime.now().isoformat(),
        }

        return _dump(
            {
                "error": False,
                "status": "success",
                "interview_id": interview_id,
                "candidate_id": candidate_id,
                "candidate_name": candidate["name"],
                "candidate_email": candidate["email"],
                "date": date,
                "time": time,
                "job_id": job_id,
                "message": f"Lịch phỏng vấn đã đặt thành công cho {candidate['name']} vào {date} lúc {time}.",
            },
            indent=2,
        )
    except Exception as exc:
        return _dump({"error": True, "code": "TOOL_EXCEPTION", "message": str(exc)})


def send_notification(candidate_id: str, notification_type: str, candidates_db: dict, booked_interviews: dict) -> str:
    """Mock an HR notification. No real email is sent."""
    try:
        allowed_types = {"interview_scheduled", "interview_reminder", "rejection"}
        if notification_type not in allowed_types:
            return _dump(
                {
                    "error": True,
                    "code": "INVALID_NOTIFICATION_TYPE",
                    "message": f"Loại thông báo '{notification_type}' không hợp lệ.",
                    "allowed_types": sorted(allowed_types),
                }
            )

        if candidate_id not in candidates_db:
            return _dump({"error": True, "code": "CANDIDATE_NOT_FOUND", "message": f"Ứng viên '{candidate_id}' không tồn tại."})

        candidate = candidates_db[candidate_id]
        interview_info = next(
            (booking for booking in booked_interviews.values() if booking["candidate_id"] == candidate_id),
            None,
        )

        if notification_type in {"interview_scheduled", "interview_reminder"} and not interview_info:
            return _dump(
                {
                    "error": True,
                    "code": "INTERVIEW_NOT_FOUND",
                    "message": f"Không tìm thấy lịch phỏng vấn cho ứng viên '{candidate_id}'.",
                }
            )

        subjects = {
            "interview_scheduled": "Lời mời phỏng vấn - Công ty XYZ",
            "interview_reminder": "Nhắc nhở phỏng vấn sắp tới",
            "rejection": "Kết quả tuyển dụng - Công ty XYZ",
        }
        return _dump(
            {
                "error": False,
                "status": "sent",
                "mock_only": True,
                "recipient": candidate["email"],
                "recipient_name": candidate["name"],
                "notification_type": notification_type,
                "subject": subjects[notification_type],
                "message": f"Mock notification '{notification_type}' đã được tạo cho {candidate['email']}.",
            },
            indent=2,
        )
    except Exception as exc:
        return _dump({"error": True, "code": "TOOL_EXCEPTION", "message": str(exc)})


def get_interview_status(candidate_id: str, candidates_db: dict, booked_interviews: dict) -> str:
    """Return the interview status for one candidate."""
    try:
        if candidate_id not in candidates_db:
            return _dump({"error": True, "code": "CANDIDATE_NOT_FOUND", "message": f"Ứng viên '{candidate_id}' không tồn tại."})
        interview_info = next(
            (booking for booking in booked_interviews.values() if booking["candidate_id"] == candidate_id),
            None,
        )
        if not interview_info:
            return _dump(
                {
                    "error": False,
                    "candidate_id": candidate_id,
                    "has_interview": False,
                    "message": f"Ứng viên {candidate_id} chưa có lịch phỏng vấn.",
                }
            )
        return _dump({"error": False, "candidate_id": candidate_id, "has_interview": True, "interview_details": interview_info}, indent=2)
    except Exception as exc:
        return _dump({"error": True, "code": "TOOL_EXCEPTION", "message": str(exc)})


AVAILABLE_TOOLS = {
    "get_candidate_profile": {
        "description": "Tra cứu hồ sơ chi tiết của ứng viên.",
        "function": get_candidate_profile,
        "parameters": {
            "type": "object",
            "properties": {"candidate_id": {"type": "string", "description": "Mã ứng viên, ví dụ CV_001."}},
            "required": ["candidate_id"],
        },
    },
    "get_job_requirements": {
        "description": "Lấy yêu cầu chi tiết của một vị trí tuyển dụng.",
        "function": get_job_requirements,
        "parameters": {
            "type": "object",
            "properties": {"job_id": {"type": "string", "description": "Mã công việc, ví dụ backend_senior."}},
            "required": ["job_id"],
        },
    },
    "evaluate_fit": {
        "description": "Đối chiếu bằng chứng CV với JD và trả tín hiệu phù hợp trung lập.",
        "function": evaluate_fit,
        "parameters": {
            "type": "object",
            "properties": {
                "candidate_id": {"type": "string"},
                "job_id": {"type": "string"},
            },
            "required": ["candidate_id", "job_id"],
        },
    },
    "check_interview_schedule": {
        "description": "Kiểm tra các slot phỏng vấn còn trống cho một ngày.",
        "function": check_interview_schedule,
        "parameters": {
            "type": "object",
            "properties": {"date": {"type": "string", "description": "Ngày dạng YYYY-MM-DD."}},
            "required": ["date"],
        },
    },
    "schedule_interview": {
        "description": "Đặt lịch phỏng vấn mock/in-memory sau khi đã có xác nhận rõ ràng.",
        "function": schedule_interview,
        "parameters": {
            "type": "object",
            "properties": {
                "candidate_id": {"type": "string"},
                "date": {"type": "string"},
                "time": {"type": "string"},
                "job_id": {"type": "string"},
                "confirmed": {"type": "boolean"},
            },
            "required": ["candidate_id", "date", "time", "job_id", "confirmed"],
        },
    },
    "send_notification": {
        "description": "Tạo thông báo mock; không gửi email thật.",
        "function": send_notification,
        "parameters": {
            "type": "object",
            "properties": {
                "candidate_id": {"type": "string"},
                "notification_type": {
                    "type": "string",
                    "enum": ["interview_scheduled", "interview_reminder", "rejection"],
                },
            },
            "required": ["candidate_id", "notification_type"],
        },
    },
    "get_interview_status": {
        "description": "Tra cứu tình trạng phỏng vấn của một ứng viên.",
        "function": get_interview_status,
        "parameters": {
            "type": "object",
            "properties": {"candidate_id": {"type": "string"}},
            "required": ["candidate_id"],
        },
    },
}
