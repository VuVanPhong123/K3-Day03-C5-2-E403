"""
📦 MOCK DATA (Nguồn dữ liệu giả lập cho Chủ đề 9: Sàng Lọc Hồ Sơ Tuyển Dụng & Hẹn Phỏng Vấn)

Chỉ chứa DATA thuần túy. Không chứa logic.
app.py sẽ import các biến này rồi TRUYỀN (Dependency Injection) vào các hàm trong tools.py,
tools.py không được import trực tiếp từ file này.
"""

from datetime import date

# ============================================================================
# CANDIDATES_DB - Hồ sơ ứng viên
# ============================================================================

CANDIDATES_DB = {
    "CV_001": {
        "name": "Nguyễn Văn A",
        "email": "nguyenvana@email.com",
        "phone": "0901234567",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git"],
        "experience_years": 4,
        "education": "Đại học Bách Khoa TP.HCM - Kỹ sư CNTT",
        "applied_job_id": "backend_senior",
        "cv_summary": "4 năm kinh nghiệm phát triển backend với Python/FastAPI, "
                       "từng xây dựng hệ thống microservices xử lý 1M+ request/ngày.",
    },
    "CV_002": {
        "name": "Trần Thị B",
        "email": "tranthib@email.com",
        "phone": "0912345678",
        "skills": ["React", "TypeScript", "Next.js", "TailwindCSS", "Figma"],
        "experience_years": 5,
        "education": "Đại học Khoa học Tự nhiên - Cử nhân CNTT",
        "applied_job_id": "frontend_lead",
        "cv_summary": "5 năm kinh nghiệm frontend, từng dẫn dắt team 4 người xây dựng "
                       "hệ thống dashboard cho doanh nghiệp fintech.",
    },
    "CV_003": {
        "name": "Lê Văn C",
        "email": "levanc@email.com",
        "phone": "0923456789",
        "skills": ["AWS", "Kubernetes", "Terraform", "CI/CD", "Linux"],
        "experience_years": 2,
        "education": "Cao đẳng FPT Polytechnic - CNTT",
        "applied_job_id": "devops_engineer",
        "cv_summary": "2 năm kinh nghiệm vận hành hạ tầng cloud AWS, triển khai "
                       "pipeline CI/CD tự động cho 10+ dự án.",
    },
}


# ============================================================================
# JOBS_DB - Yêu cầu vị trí tuyển dụng
# ============================================================================

JOBS_DB = {
    "backend_senior": {
        "title": "Senior Backend Engineer",
        "department": "Engineering",
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
        "experience_min": 3,
        "salary_range": "25,000,000 - 40,000,000 VNĐ",
        "location": "TP.HCM (Hybrid)",
        "description": "Xây dựng và tối ưu hệ thống backend quy mô lớn, thiết kế API "
                        "và làm việc với microservices.",
    },
    "frontend_lead": {
        "title": "Frontend Lead",
        "department": "Engineering",
        "required_skills": ["React", "TypeScript", "Next.js", "TailwindCSS"],
        "experience_min": 4,
        "salary_range": "30,000,000 - 45,000,000 VNĐ",
        "location": "Hà Nội (Onsite)",
        "description": "Dẫn dắt đội ngũ frontend, xây dựng hệ thống UI component "
                        "và định hướng kiến trúc frontend.",
    },
    "devops_engineer": {
        "title": "DevOps Engineer",
        "department": "Infrastructure",
        "required_skills": ["AWS", "Kubernetes", "Terraform", "CI/CD", "Docker"],
        "experience_min": 2,
        "salary_range": "20,000,000 - 32,000,000 VNĐ",
        "location": "TP.HCM (Remote)",
        "description": "Quản lý hạ tầng cloud, xây dựng pipeline CI/CD, đảm bảo "
                        "uptime và bảo mật hệ thống.",
    },
}


# ============================================================================
# INTERVIEW_SCHEDULE - Các slot phỏng vấn khả dụng theo ngày
# (Dùng ngày tương lai cố định để tránh lệch so với "today" khi chạy thực tế)
# ============================================================================

INTERVIEW_SCHEDULE = {
    "2026-08-05": ["09:00", "10:00", "14:00", "15:00"],
    "2026-08-06": ["09:00", "11:00", "13:30", "16:00"],
    "2026-08-07": ["10:00", "14:00", "15:30"],
}


# ============================================================================
# BOOKED_INTERVIEWS - Lịch đã đặt (dict rỗng ban đầu, sẽ được cập nhật khi
# schedule_interview() chạy trong phiên làm việc của app.py)
# ============================================================================

BOOKED_INTERVIEWS = {
    "INT_001": {
        "candidate_id": "CV_002",
        "candidate_name": "Trần Thị B",
        "candidate_email": "tranthib@email.com",
        "job_id": "frontend_lead",
        "date": "2026-08-05",
        "time": "10:00",
        "status": "confirmed",
    },
}
