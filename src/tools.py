"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Nơi khai báo tất cả các "món đồ nghề" mà ReAct Agent có thể gọi.

Chủ Đề 9: Trợ Lý Sàng Lọc Hồ Sơ Tuyển Dụng & Hẹn Phỏng Vấn

ARCHITECTURE:
- tools.py: Pure logic (không import data)
- app.py: Dependency Injection (truyền data vào tools)
- mock_data.py: Chỉ chứa data định nghĩa
"""

import json
from datetime import datetime


# ============================================================================
# TOOLS (Pure Functions - Không phụ thuộc vào data source)
# ============================================================================

def get_candidate_profile(candidate_id: str, candidates_db: dict) -> str:
    """
    Tra cứu hồ sơ chi tiết của ứng viên từ database.

    Args:
        candidate_id (str): Mã ứng viên (VD: CV_001, CV_002, CV_003)
        candidates_db (dict): Database ứng viên (truyền từ app.py)

    Returns:
        str: JSON chuỗi chứa thông tin ứng viên hoặc thông báo lỗi.

    Example:
        >>> get_candidate_profile("CV_001", CANDIDATES_DB)
        '{"name": "Nguyễn Văn A", "skills": ["Python", "FastAPI"], ...}'
    """
    try:
        if candidate_id not in candidates_db:
            return json.dumps({
                "error": True,
                "message": f"LỖI: Không tìm thấy hồ sơ ứng viên '{candidate_id}'."
            }, ensure_ascii=False)

        profile = candidates_db[candidate_id]
        return json.dumps({
            "error": False,
            "candidate_id": candidate_id,
            "data": profile
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"LỖI Exception: {str(e)}"
        }, ensure_ascii=False)


def get_job_requirements(job_id: str, jobs_db: dict) -> str:
    """
    Lấy yêu cầu chi tiết của một vị trí tuyển dụng.

    Args:
        job_id (str): Mã công việc (VD: backend_senior, frontend_lead)
        jobs_db (dict): Database công việc (truyền từ app.py)

    Returns:
        str: JSON chuỗi chứa thông tin công việc hoặc thông báo lỗi.

    Example:
        >>> get_job_requirements("backend_senior", JOBS_DB)
        '{"title": "Senior Backend Engineer", "required_skills": [...], ...}'
    """
    try:
        if job_id not in jobs_db:
            return json.dumps({
                "error": True,
                "message": f"LỖI: Không tìm thấy công việc '{job_id}'."
            }, ensure_ascii=False)

        job = jobs_db[job_id]
        return json.dumps({
            "error": False,
            "job_id": job_id,
            "data": job
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"LỖI Exception: {str(e)}"
        }, ensure_ascii=False)


def evaluate_fit(candidate_id: str, job_id: str, candidates_db: dict, jobs_db: dict) -> str:
    """
    Đánh giá mức độ phù hợp (%) giữa ứng viên và công việc.
    Dựa trên: kỹ năng, kinh nghiệm, và yêu cầu công việc.

    Args:
        candidate_id (str): Mã ứng viên
        job_id (str): Mã công việc
        candidates_db (dict): Database ứng viên
        jobs_db (dict): Database công việc

    Returns:
        str: JSON chứa phần trăm phù hợp, phân tích chi tiết, và khuyến nghị.

    Example:
        >>> evaluate_fit("CV_001", "backend_senior", CANDIDATES_DB, JOBS_DB)
        '{"fit_percentage": 92, "matched_skills": [...], ...}'
    """
    try:
        if candidate_id not in candidates_db:
            return json.dumps({
                "error": True,
                "message": f"LỖI: Ứng viên '{candidate_id}' không tồn tại."
            }, ensure_ascii=False)

        if job_id not in jobs_db:
            return json.dumps({
                "error": True,
                "message": f"LỖI: Công việc '{job_id}' không tồn tại."
            }, ensure_ascii=False)

        candidate = candidates_db[candidate_id]
        job = jobs_db[job_id]

        candidate_skills = set(skill.lower() for skill in candidate["skills"])
        required_skills = set(skill.lower() for skill in job["required_skills"])

        matched_skills = candidate_skills & required_skills
        missing_skills = required_skills - candidate_skills

        skill_score = len(matched_skills) / len(required_skills) * 100 if required_skills else 0
        exp_score = min(100, (candidate["experience_years"] / job["experience_min"]) * 100) if job["experience_min"] > 0 else 100

        fit_percentage = int((skill_score + exp_score) / 2)

        if fit_percentage >= 85:
            recommendation = "🟢 RẤT PHÙ HỢP - Ưu tiên phỏng vấn"
        elif fit_percentage >= 70:
            recommendation = "🟡 PHÙ HỢP - Xem xét phỏng vấn"
        elif fit_percentage >= 50:
            recommendation = "🟠 TƯƠNG ĐỐI PHÙ HỢP - Có thể phỏng vấn nhưng chưa lý tưởng"
        else:
            recommendation = "🔴 KHÔNG PHÙ HỢP - Không khuyến nghị"

        return json.dumps({
            "error": False,
            "candidate_id": candidate_id,
            "job_id": job_id,
            "fit_percentage": fit_percentage,
            "matched_skills": list(matched_skills),
            "missing_skills": list(missing_skills),
            "skill_score": round(skill_score, 1),
            "experience_score": round(exp_score, 1),
            "recommendation": recommendation,
            "candidate_experience": candidate["experience_years"],
            "job_required_experience": job["experience_min"],
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"LỖI Exception: {str(e)}"
        }, ensure_ascii=False)


def check_interview_schedule(date: str, interview_schedule: dict, booked_interviews: dict) -> str:
    """
    Kiểm tra các slot phỏng vấn còn trống cho một ngày cụ thể.

    Args:
        date (str): Ngày cần kiểm tra (format: YYYY-MM-DD, VD: 2026-08-05)
        interview_schedule (dict): Lịch phỏng vấn khả dụng
        booked_interviews (dict): Lịch đã đặt

    Returns:
        str: JSON chứa danh sách các slot còn trống hoặc thông báo lỗi.

    Example:
        >>> check_interview_schedule("2026-08-05", INTERVIEW_SCHEDULE, BOOKED_INTERVIEWS)
        '{"date": "2026-08-05", "available_slots": ["09:00", "10:00", ...], ...}'
    """
    try:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return json.dumps({
                "error": True,
                "message": f"LỖI: Định dạng ngày không hợp lệ '{date}'. Vui lòng dùng format YYYY-MM-DD (VD: 2026-08-05)."
            }, ensure_ascii=False)

        today = datetime.now().strftime("%Y-%m-%d")
        if date < today:
            return json.dumps({
                "error": True,
                "message": f"LỖI: Không thể đặt lịch trong quá khứ. Ngày yêu cầu: {date}, Ngày hôm nay: {today}."
            }, ensure_ascii=False)

        if date not in interview_schedule:
            return json.dumps({
                "error": True,
                "message": f"LỖI: Không có lịch phỏng vấn cho ngày {date}. Hãy chọn từ các ngày: {', '.join(sorted(interview_schedule.keys()))}.",
                "available_dates": sorted(interview_schedule.keys())
            }, ensure_ascii=False)

        all_slots = interview_schedule[date]
        booked_slots = [
            booked["time"]
            for booked in booked_interviews.values()
            if booked["date"] == date
        ]
        available_slots = [slot for slot in all_slots if slot not in booked_slots]

        return json.dumps({
            "error": False,
            "date": date,
            "available_slots": available_slots,
            "booked_slots": booked_slots,
            "total_slots": len(all_slots),
            "available_count": len(available_slots),
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"LỖI Exception: {str(e)}"
        }, ensure_ascii=False)


def schedule_interview(candidate_id: str, date: str, time: str, job_id: str,
                      candidates_db: dict, interview_schedule: dict, booked_interviews: dict) -> str:
    """
    Đặt lịch phỏng vấn cho ứng viên ở slot và ngày cụ thể.

    Args:
        candidate_id (str): Mã ứng viên (VD: CV_001)
        date (str): Ngày phỏng vấn (format: YYYY-MM-DD, VD: 2026-08-05)
        time (str): Giờ phỏng vấn (format: HH:MM, VD: 09:00)
        job_id (str): Mã công việc (optional)
        candidates_db (dict): Database ứng viên
        interview_schedule (dict): Lịch phỏng vấn khả dụng
        booked_interviews (dict): Lịch đã đặt (sẽ được cập nhật)

    Returns:
        str: JSON xác nhận lịch phỏng vấn hoặc thông báo lỗi.

    Example:
        >>> schedule_interview("CV_001", "2026-08-05", "09:00", "backend_senior", ...)
        '{"status": "success", "interview_id": "INT_001", ...}'
    """
    try:
        if candidate_id not in candidates_db:
            return json.dumps({
                "error": True,
                "message": f"LỖI: Ứng viên '{candidate_id}' không tồn tại."
            }, ensure_ascii=False)

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return json.dumps({
                "error": True,
                "message": f"LỖI: Định dạng ngày không hợp lệ '{date}'. Vui lòng dùng YYYY-MM-DD."
            }, ensure_ascii=False)

        try:
            datetime.strptime(time, "%H:%M")
        except ValueError:
            return json.dumps({
                "error": True,
                "message": f"LỖI: Định dạng giờ không hợp lệ '{time}'. Vui lòng dùng HH:MM."
            }, ensure_ascii=False)

        if date not in interview_schedule:
            return json.dumps({
                "error": True,
                "message": f"LỖI: Không có lịch cho ngày {date}. Các ngày hợp lệ: {', '.join(sorted(interview_schedule.keys()))}."
            }, ensure_ascii=False)

        if time not in interview_schedule[date]:
            return json.dumps({
                "error": True,
                "message": f"LỖI: Giờ {time} không có trong lịch ngày {date}. Các giờ hợp lệ: {', '.join(interview_schedule[date])}."
            }, ensure_ascii=False)

        for booking in booked_interviews.values():
            if booking["date"] == date and booking["time"] == time:
                return json.dumps({
                    "error": True,
                    "message": f"LỖI: Slot {time} ngày {date} đã bị đặt bởi {booking['candidate_id']}. Vui lòng chọn slot khác."
                }, ensure_ascii=False)

        interview_id = f"INT_{len(booked_interviews) + 1:03d}"
        candidate_name = candidates_db[candidate_id]["name"]
        candidate_email = candidates_db[candidate_id]["email"]

        booked_interviews[interview_id] = {
            "candidate_id": candidate_id,
            "candidate_name": candidate_name,
            "date": date,
            "time": time,
            "job_id": job_id,
            "status": "confirmed",
            "booked_at": datetime.now().isoformat(),
        }

        return json.dumps({
            "error": False,
            "status": "success",
            "interview_id": interview_id,
            "candidate_id": candidate_id,
            "candidate_name": candidate_name,
            "candidate_email": candidate_email,
            "date": date,
            "time": time,
            "job_id": job_id,
            "message": f"✅ Lịch phỏng vấn đã đặt thành công cho {candidate_name} vào {date} lúc {time}."
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"LỖI Exception: {str(e)}"
        }, ensure_ascii=False)


def send_notification(candidate_id: str, notification_type: str,
                     candidates_db: dict, booked_interviews: dict) -> str:
    """
    Gửi thông báo/lời mời phỏng vấn cho ứng viên qua email.

    Args:
        candidate_id (str): Mã ứng viên (VD: CV_001)
        notification_type (str): Loại thông báo ('interview_scheduled', 'interview_reminder', 'rejection')
        candidates_db (dict): Database ứng viên
        booked_interviews (dict): Lịch đã đặt

    Returns:
        str: JSON xác nhận gửi thông báo hoặc thông báo lỗi.

    Example:
        >>> send_notification("CV_001", "interview_scheduled", CANDIDATES_DB, BOOKED_INTERVIEWS)
        '{"status": "sent", "recipient": "nguyenvana@email.com", ...}'
    """
    try:
        if candidate_id not in candidates_db:
            return json.dumps({
                "error": True,
                "message": f"LỖI: Ứng viên '{candidate_id}' không tồn tại."
            }, ensure_ascii=False)

        candidate = candidates_db[candidate_id]
        email = candidate["email"]
        name = candidate["name"]

        interview_info = None
        for booking in booked_interviews.values():
            if booking["candidate_id"] == candidate_id:
                interview_info = booking
                break

        if notification_type == "interview_scheduled":
            if not interview_info:
                return json.dumps({
                    "error": True,
                    "message": f"LỖI: Không tìm thấy lịch phỏng vấn cho ứng viên '{candidate_id}'."
                }, ensure_ascii=False)

            subject = "Lời mời phỏng vấn - Công ty XYZ"
            message_body = f"""Xin chào {name},

Chúng tôi rất vui nhận được ứng tuyển của bạn.
Sau khi xem xét hồ sơ, chúng tôi muốn mời bạn tham gia phỏng vấn.

Thông tin phỏng vấn:
- Ngày: {interview_info['date']}
- Giờ: {interview_info['time']}
- Vị trí: {interview_info.get('job_id', 'TBD')}

Vui lòng xác nhận tham dự bằng cách reply email này.

Trân trọng,
Bộ phận HR"""

        elif notification_type == "rejection":
            subject = "Kết quả tuyển dụng - Công ty XYZ"
            message_body = f"""Xin chào {name},

Cảm ơn bạn đã ứng tuyển vị trí tại công ty chúng tôi.
Dù hồ sơ của bạn xuất sắc, nhưng lần này chúng tôi quyết định chọn ứng viên khác.

Chúng tôi hy vọng có cơ hội hợp tác với bạn trong tương lai.

Trân trọng,
Bộ phận HR"""

        else:
            if not interview_info:
                return json.dumps({
                    "error": True,
                    "message": f"LỖI: Không tìm thấy lịch phỏng vấn cho ứng viên '{candidate_id}' để gửi nhắc nhở."
                }, ensure_ascii=False)

            subject = "Nhắc nhở - Phỏng vấn sắp tới"
            message_body = f"""Xin chào {name},

Nhắc nhở: Phỏng vấn của bạn sẽ diễn ra vào:
- Ngày: {interview_info['date']}
- Giờ: {interview_info['time']}

Vui lòng chuẩn bị tốt và đến sớm 10 phút trước giờ phỏng vấn.

Trân trọng,
Bộ phận HR"""

        return json.dumps({
            "error": False,
            "status": "sent",
            "recipient": email,
            "recipient_name": name,
            "notification_type": notification_type,
            "subject": subject,
            "body_preview": message_body[:100] + "..." if len(message_body) > 100 else message_body,
            "message": f"✅ Thông báo '{notification_type}' đã gửi tới {email}."
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"LỖI Exception: {str(e)}"
        }, ensure_ascii=False)


def get_interview_status(candidate_id: str, candidates_db: dict, booked_interviews: dict) -> str:
    """
    Tra cứu tình trạng phỏng vấn của một ứng viên.

    Args:
        candidate_id (str): Mã ứng viên (VD: CV_001)
        candidates_db (dict): Database ứng viên
        booked_interviews (dict): Lịch đã đặt

    Returns:
        str: JSON chứa thông tin lịch phỏng vấn hoặc thông báo không có.

    Example:
        >>> get_interview_status("CV_001", CANDIDATES_DB, BOOKED_INTERVIEWS)
        '{"candidate_id": "CV_001", "has_interview": true, "interview_details": {...}}'
    """
    try:
        if candidate_id not in candidates_db:
            return json.dumps({
                "error": True,
                "message": f"LỖI: Ứng viên '{candidate_id}' không tồn tại."
            }, ensure_ascii=False)

        interview_info = None
        for booking in booked_interviews.values():
            if booking["candidate_id"] == candidate_id:
                interview_info = booking
                break

        if not interview_info:
            return json.dumps({
                "error": False,
                "candidate_id": candidate_id,
                "has_interview": False,
                "message": f"Ứng viên {candidate_id} chưa có lịch phỏng vấn được đặt."
            }, ensure_ascii=False)

        return json.dumps({
            "error": False,
            "candidate_id": candidate_id,
            "has_interview": True,
            "interview_details": interview_info
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"LỖI Exception: {str(e)}"
        }, ensure_ascii=False)


# ============================================================================
# TOOL REGISTRY - Đăng ký các công cụ để Agent sử dụng
# ============================================================================

AVAILABLE_TOOLS = {
    "get_candidate_profile": {
        "description": "Tra cứu hồ sơ chi tiết của ứng viên (tên, email, kỹ năng, kinh nghiệm, bằng cấp)",
        "function": get_candidate_profile,
        "parameters": {
            "type": "object",
            "properties": {
                "candidate_id": {
                    "type": "string",
                    "description": "Mã ứng viên (VD: CV_001, CV_002, CV_003)"
                }
            },
            "required": ["candidate_id"]
        }
    },
    "get_job_requirements": {
        "description": "Lấy yêu cầu chi tiết của một vị trí tuyển dụng",
        "function": get_job_requirements,
        "parameters": {
            "type": "object",
            "properties": {
                "job_id": {
                    "type": "string",
                    "description": "Mã công việc (VD: backend_senior, frontend_lead, devops_engineer)"
                }
            },
            "required": ["job_id"]
        }
    },
    "evaluate_fit": {
        "description": "Đánh giá mức độ phù hợp (%) giữa ứng viên và công việc dựa trên kỹ năng và kinh nghiệm",
        "function": evaluate_fit,
        "parameters": {
            "type": "object",
            "properties": {
                "candidate_id": {
                    "type": "string",
                    "description": "Mã ứng viên"
                },
                "job_id": {
                    "type": "string",
                    "description": "Mã công việc"
                }
            },
            "required": ["candidate_id", "job_id"]
        }
    },
    "check_interview_schedule": {
        "description": "Kiểm tra các slot phỏng vấn còn trống cho một ngày cụ thể",
        "function": check_interview_schedule,
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Ngày cần kiểm tra (format: YYYY-MM-DD, VD: 2026-08-05)"
                }
            },
            "required": ["date"]
        }
    },
    "schedule_interview": {
        "description": "Đặt lịch phỏng vấn cho ứng viên ở slot ngày/giờ cụ thể",
        "function": schedule_interview,
        "parameters": {
            "type": "object",
            "properties": {
                "candidate_id": {
                    "type": "string",
                    "description": "Mã ứng viên"
                },
                "date": {
                    "type": "string",
                    "description": "Ngày phỏng vấn (format: YYYY-MM-DD)"
                },
                "time": {
                    "type": "string",
                    "description": "Giờ phỏng vấn (format: HH:MM)"
                },
                "job_id": {
                    "type": "string",
                    "description": "Mã công việc (optional)"
                }
            },
            "required": ["candidate_id", "date", "time"]
        }
    },
    "send_notification": {
        "description": "Gửi thông báo/lời mời phỏng vấn cho ứng viên qua email",
        "function": send_notification,
        "parameters": {
            "type": "object",
            "properties": {
                "candidate_id": {
                    "type": "string",
                    "description": "Mã ứng viên"
                },
                "notification_type": {
                    "type": "string",
                    "description": "Loại thông báo: 'interview_scheduled', 'interview_reminder', 'rejection'"
                }
            },
            "required": ["candidate_id"]
        }
    },
    "get_interview_status": {
        "description": "Tra cứu tình trạng phỏng vấn của một ứng viên",
        "function": get_interview_status,
        "parameters": {
            "type": "object",
            "properties": {
                "candidate_id": {
                    "type": "string",
                    "description": "Mã ứng viên"
                }
            },
            "required": ["candidate_id"]
        }
    },
}
