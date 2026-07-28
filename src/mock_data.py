"""
🗄️ MOCK DATABASE CHO HỆ THỐNG TUYỂN DỤNG & PHỎNG VẤN
Dữ liệu mẫu phục vụ kiểm thử cho 15 Test Cases.
"""

CANDIDATES_DB = {
    "CV_001": {
        "name": "Nguyễn Văn A",
        "email": "nguyenvana@email.com",
        "position": "Backend Developer",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "REST API"],
        "experience_years": 3,
        "education": "Đại học Bách Khoa (Tốt nghiệp 2021)",
        "summary": "Lập trình viên Backend 3 năm kinh nghiệm phát triển RESTful API với Python & FastAPI."
    },
    "CV_002": {
        "name": "Trần Thị B",
        "email": "tranthib@email.com",
        "position": "Frontend Lead",
        "skills": ["React", "TypeScript", "Next.js", "Tailwind CSS", "Redux"],
        "experience_years": 5,
        "education": "Đại học Công nghệ (Tốt nghiệp 2019)",
        "summary": "Frontend Lead với 5 năm kinh nghiệm làm việc với React và TypeScript."
    },
    "CV_003": {
        "name": "Lê Văn C",
        "email": "levanc@email.com",
        "position": "Backend Developer",
        "skills": ["Java", "Spring Boot", "PostgreSQL", "Docker", "Microservices"],
        "experience_years": 4,
        "education": "Đại học Bách Khoa (Tốt nghiệp 2020)",
        "summary": "Backend Engineer chuyên Java Spring Boot và hệ thống Microservices."
    },
    "CV_004": {
        "name": "Phạm Văn D",
        "email": "phamvand@email.com",
        "position": "Data Analyst",
        "skills": ["Python", "SQL", "Tableau", "PowerBI", "Pandas"],
        "experience_years": 2,
        "education": "Đại học Kinh tế Quốc dân (Tốt nghiệp 2022)",
        "summary": "Data Analyst 2 năm kinh nghiệm trực quan hóa dữ liệu và xây dựng dashboard."
    },
    "CV_005": {
        "name": "Hoàng Văn E",
        "email": "hoangvane@email.com",
        "position": "Senior Backend Engineer",
        "skills": ["Java", "Spring Boot", "Microservices", "Kafka", "Kubernetes", "Redis"],
        "experience_years": 5,
        "education": "Đại học Bách Khoa (Tốt nghiệp 2020)",
        "summary": "Senior Java Developer có 5 năm kinh nghiệm làm việc với hệ thống lớn."
    },
    "CV_006": {
        "name": "Nguyễn Thị F",
        "email": "nguyenthif@email.com",
        "position": "Backend Developer",
        "skills": ["Java", "Spring Boot", "MySQL", "Docker"],
        "experience_years": 3,
        "education": "Đại học Bách Khoa (Tốt nghiệp 2021)",
        "summary": "Java Developer 3 năm kinh nghiệm."
    }
}

JOBS_DB = {
    "backend_senior": {
        "title": "Senior Backend Engineer",
        "department": "Engineering",
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
        "experience_min": 3,
        "description": "Phát triển và tối ưu hóa hệ thống backend microservices."
    },
    "backend_java_senior": {
        "title": "Senior Java Backend Engineer",
        "department": "Engineering",
        "required_skills": ["Java", "Spring Boot", "PostgreSQL", "Microservices"],
        "experience_min": 3,
        "description": "Xây dựng các ứng dụng Java Enterprise."
    },
    "frontend_lead": {
        "title": "Frontend Lead",
        "department": "Engineering",
        "required_skills": ["React", "TypeScript", "Next.js"],
        "experience_min": 4,
        "description": "Dẫn dắt đội ngũ Frontend phát triển sản phẩm Web App."
    },
    "data_analyst": {
        "title": "Data Analyst",
        "department": "Data Science",
        "required_skills": ["Python", "SQL", "Tableau"],
        "experience_min": 2,
        "description": "Phân tích dữ liệu kinh doanh và báo cáo cho ban quản trị."
    }
}

INTERVIEW_SCHEDULE = {
    "2026-08-04": ["09:00", "10:00", "14:00", "15:00"],
    "2026-08-05": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"],
    "2026-08-06": ["09:00", "10:00", "14:00", "15:00"],
    "2026-08-11": ["09:00", "10:00", "11:00", "14:00", "15:00"]
}

BOOKED_INTERVIEWS = {
    "INT_001": {
        "candidate_id": "CV_001",
        "candidate_name": "Nguyễn Văn A",
        "date": "2026-08-05",
        "time": "09:00",
        "job_id": "backend_senior",
        "status": "confirmed",
        "booked_at": "2026-07-28T09:00:00"
    }
}
