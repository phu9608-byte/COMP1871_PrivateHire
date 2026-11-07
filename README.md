# COMP1871 – PrivateHire

Hệ thống đặt xe (private hire) cho khách hàng và tài xế – coursework COMP1807 Agile Development with SCRUM.

| Thư mục | Nội dung |
|---|---|
| [`backend/`](backend/) | REST API – Python (FastAPI) + PostgreSQL |

## Chạy dự án

Có **2 cách**, chọn 1 là đủ (chạy song song cũng được):

| | A – Chạy trên máy | B – Chạy bằng Docker |
|---|---|---|
| Dùng khi | Đang code, chạy test | Demo / chỉ muốn chạy thử |
| Cần cài | Python + PostgreSQL | Docker Desktop |
| Swagger | http://127.0.0.1:8000/docs | http://127.0.0.1:8080/docs |
| Hướng dẫn | [backend/README.md – mục 1](backend/README.md#1-cách-a--chạy-trên-máy-khi-code) | [backend/README.md – mục 2](backend/README.md#2-cách-b--chạy-bằng-docker-khi-demo) |

**Đã cài đặt xong, chỉ cần bật lên:**

```powershell
# Cách A – trong thư mục backend\
.venv\Scripts\fastapi dev app/main.py     # bật server
.venv\Scripts\pytest -v                   # chạy test

# Cách B – ở thư mục gốc (mở Docker Desktop trước)
docker compose up -d --build              # bật / cập nhật sau khi sửa code
docker compose down                       # tắt (dữ liệu vẫn còn)
```

Hướng dẫn đầy đủ (cài đặt, quy trình làm việc, API, database, pgAdmin, lỗi thường gặp): [`backend/README.md`](backend/README.md).