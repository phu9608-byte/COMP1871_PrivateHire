# PrivateHire – Backend

REST API cho hệ thống đặt xe PrivateHire.

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ | Python 3.12+ |
| Framework | FastAPI (tự sinh tài liệu Swagger) |
| Database | PostgreSQL |
| ORM / Migration | SQLAlchemy 2 + Alembic |
| Mã hoá mật khẩu | bcrypt |
| Test | pytest |

> Hướng dẫn viết cho **Windows 10/11**, mọi lệnh gõ trong **PowerShell**.

## Mục lục

0. [Hai cách chạy – đọc trước](#0-hai-cách-chạy--đọc-trước)
1. [Cách A – Chạy trên máy (khi code)](#1-cách-a--chạy-trên-máy-khi-code)
2. [Cách B – Chạy bằng Docker (khi demo)](#2-cách-b--chạy-bằng-docker-khi-demo)
3. [Quy trình làm việc hằng ngày](#3-quy-trình-làm-việc-hằng-ngày)
4. [API hiện có](#4-api-hiện-có)
5. [Database và migration](#5-database-và-migration)
6. [Xem dữ liệu bằng pgAdmin 4](#6-xem-dữ-liệu-bằng-pgadmin-4)
7. [Cấu trúc thư mục](#7-cấu-trúc-thư-mục)
8. [Lỗi thường gặp](#8-lỗi-thường-gặp)

---

## 0. Hai cách chạy – đọc trước

Cùng một backend có thể chạy theo **2 cách độc lập**. Không bắt buộc dùng cả hai.

| | **A – Chạy trên máy** | **B – Chạy bằng Docker** |
|---|---|---|
| Dùng khi | Đang code, chạy test | Demo, hoặc bạn trong nhóm chỉ muốn chạy thử |
| Cần cài | Python + PostgreSQL | Chỉ Docker Desktop |
| Lệnh bật | `.venv\Scripts\fastapi dev app/main.py` (trong `backend\`) | `docker compose up -d --build` (ở thư mục gốc) |
| Swagger | http://127.0.0.1:8000/docs | http://127.0.0.1:8080/docs |
| PostgreSQL | Cài trên máy, cổng **5432** | Trong Docker, cổng **5433** |
| File cấu hình | `backend\.env` | `.env` ở **thư mục gốc** |
| Sửa code xong | Server tự reload | Phải build lại |
| Chạy test | Có (`pytest`) | Không |

- Hai cách dùng **2 database riêng**: tài khoản đăng ký bên này không có bên kia.
- Hai cách **chạy song song được** vì không trùng cổng.
- Hai file `.env` là **hai file khác nhau**, đều không bị commit (đã có trong `.gitignore`). Đừng xoá `backend\.env` nếu còn chạy test.

---

## 1. Cách A – Chạy trên máy (khi code)

### 1.1. Cài phần mềm (một lần)

| Phần mềm | Tải ở đâu | Ghi chú |
|---|---|---|
| Python 3.12+ | https://www.python.org/downloads/windows/ | Tick **Add python.exe to PATH** khi cài |
| PostgreSQL | https://www.postgresql.org/download/windows/ | Bộ cài có sẵn **pgAdmin 4** và **psql** |

Khi cài PostgreSQL: **ghi lại mật khẩu của tài khoản `postgres`**, để cổng mặc định `5432`, giữ thành phần **pgAdmin 4** và **Command Line Tools**.

Thêm `psql` vào PATH (thay `18` bằng phiên bản bạn cài):

```powershell
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path","User") + ";C:\Program Files\PostgreSQL\18\bin", "User")
```

**Đóng PowerShell, mở lại**, rồi kiểm tra:

```powershell
python --version
psql --version
Get-Service postgresql*      # Status phải là Running
```

> - `Get-Service` không in ra gì → chưa cài PostgreSQL.
> - `Status` là `Running` → xong, **không cần** `Start-Service`.
> - `Status` là `Stopped` → mở PowerShell **quyền Admin**, chạy `Start-Service postgresql-x64-18`.

### 1.2. Tạo tài khoản và database (một lần)

```powershell
psql -U postgres             # nhập mật khẩu postgres đặt lúc cài
```

Tại dấu nhắc `postgres=#`, dán cả khối (thay `MAT_KHAU_CUA_BAN` bằng mật khẩu bạn chọn, chỉ dùng chữ và số):

```sql
CREATE ROLE privatehire LOGIN PASSWORD 'MAT_KHAU_CUA_BAN';
CREATE DATABASE privatehire OWNER privatehire;
CREATE DATABASE privatehire_test OWNER privatehire;
\l privatehire*
\q
```

> - psql chạy **từng câu** ngay khi gặp dấu `;`. Lỡ chạy trùng một câu thì nó báo `already exists` – vô hại.
> - Đổi mật khẩu sau này: `ALTER ROLE privatehire PASSWORD 'moi';`
> - Dấu nhắc thành `postgres-#` nghĩa là còn lệnh gõ dở → gõ `\r` để xoá.

### 1.3. Cài thư viện Python (một lần)

```powershell
cd backend
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
```

> `requirements.txt` = thư viện để chạy (dùng trong Docker). `requirements-dev.txt` = thêm thư viện test.

> **Không cần kích hoạt venv** – hướng dẫn luôn ghi đầy đủ `.venv\Scripts\...`.
> Nếu muốn kích hoạt (`.venv\Scripts\Activate.ps1`) mà bị báo `running scripts is disabled`, chạy một lần
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

### 1.4. Tạo file `backend\.env` (một lần)

```powershell
Copy-Item .env.example .env
notepad .env
```

Thay `DOI_MAT_KHAU` bằng mật khẩu đã đặt ở bước 1.2 (**cả 2 dòng**), rồi lưu:

```env
DATABASE_URL=postgresql+psycopg://privatehire:MAT_KHAU_CUA_BAN@localhost:5432/privatehire
TEST_DATABASE_URL=postgresql+psycopg://privatehire:MAT_KHAU_CUA_BAN@localhost:5432/privatehire_test
```

### 1.5. Tạo bảng

```powershell
.venv\Scripts\alembic upgrade head
```

Chạy lại lệnh này mỗi khi kéo code mới có migration mới.

### 1.6. Dùng hằng ngày

Tất cả chạy trong thư mục `backend\`.

**Bật server** (sửa code là tự reload, dừng bằng **Ctrl + C**):

```powershell
.venv\Scripts\fastapi dev app/main.py
```

- Swagger: http://127.0.0.1:8000/docs
- Kiểm tra server: http://127.0.0.1:8000/health

**Chạy test** (không cần bật server, không cần tắt Docker):

```powershell
.venv\Scripts\pytest -v
```

| Database | Ai dùng | Trong pgAdmin |
|---|---|---|
| `privatehire` | Server / Swagger | Có bảng `users` và dữ liệu bạn đăng ký |
| `privatehire_test` | Chỉ `pytest` | **Trống** – test tự tạo bảng, chạy xong tự xoá |

Test không bao giờ đụng vào dữ liệu trong `privatehire`.

---

## 2. Cách B – Chạy bằng Docker (khi demo)

Docker chạy cả PostgreSQL lẫn backend, **tự tạo bảng và tự bật server** – không cần Python, `.venv`, `alembic` hay `fastapi dev`.

**Mở Docker Desktop trước**, chờ góc dưới trái báo **Engine running**.

### 2.1. Lần đầu

Mọi lệnh chạy ở **thư mục gốc** (chỗ có `docker-compose.yml`), **không phải** `backend\`.

```powershell
Copy-Item .env.example .env
notepad .env                 # sửa POSTGRES_PASSWORD (chỉ chữ và số) rồi lưu
docker compose up -d --build
```

> Tạo mật khẩu ngẫu nhiên: `python -c "import secrets; print(secrets.token_hex(16))"`

Lần đầu mất vài phút. Xong thì:

- Swagger: http://127.0.0.1:8080/docs
- Trong Docker Desktop → **Containers** có nhóm **`comp1807_privatehire`** (bấm `>` để thấy `db` và `backend`).
- PostgreSQL trong Docker: `localhost:5433`, user `privatehire`, mật khẩu = `POSTGRES_PASSWORD`.

Khi khởi động, container `backend` tự chạy `alembic upgrade head` rồi `fastapi run app/main.py`.

### 2.2. Lệnh hay dùng

| Lệnh | Tác dụng |
|---|---|
| `docker compose up -d --build` | Build lại (sau khi sửa code) và chạy nền |
| `docker compose ps` | Xem trạng thái container |
| `docker compose logs -f backend` | Xem log backend (Ctrl+C để thoát) |
| `docker compose down` | Tắt (**dữ liệu vẫn còn** trong volume `pgdata`) |
| `docker compose down -v` | Tắt và **xoá luôn dữ liệu** – cẩn thận! |
| `docker compose exec db psql -U privatehire -d privatehire` | Mở psql vào database trong Docker |

> - Build lại chỉ tạo mới container `backend` (mất vài giây), dữ liệu database giữ nguyên.
> - Docker chỉ mở cổng trên `127.0.0.1` → **chỉ máy của bạn** truy cập được.
> - Không dùng thì tắt (`docker compose down` hoặc Quit Docker Desktop) cho nhẹ máy – Docker Desktop tốn 1–2 GB RAM.

---

## 3. Quy trình làm việc hằng ngày

```
 ┌─ Docker (8080): bản ổn định để demo – có thể tắt cho nhẹ máy
 │
 └─ Trên máy (8000): nơi code
      1. git checkout -b feature/ten-tinh-nang
      2. sửa code + viết test trong tests/
      3. .venv\Scripts\fastapi dev app/main.py   → thử trên Swagger
      4. .venv\Scripts\pytest -v                  → tất cả phải pass
      5. commit, push, tạo Pull Request → merge vào main
      6. (nếu cần demo) docker compose up -d --build   ← ở thư mục gốc
```

- Ai làm tính năng nào thì viết test cho tính năng đó (vd. `tests/test_login.py`).
- Thêm/sửa bảng → tạo migration (mục 5), đừng sửa bằng pgAdmin.

---

## 4. API hiện có

### `POST /api/v1/auth/register` – Đăng ký tài khoản

**Body:**

```json
{
  "username": "an.nguyen",
  "email": "an.nguyen@example.com",
  "password": "matkhau12345",
  "full_name": "Nguyen Van An",
  "phone": "0901234567",
  "marketing_consent": false,
  "role": "customer"
}
```

| Trường | Bắt buộc | Quy tắc |
|---|---|---|
| `username` | ✔ | 3–30 ký tự, chỉ chữ không dấu, số, `_` và `.`; tự chuyển về chữ thường; không được trùng |
| `email` | ✔ | Đúng định dạng email, tự chuyển về chữ thường, không được trùng |
| `password` | ✔ | **Từ 12 ký tự**, tối đa 72 byte; lưu dạng băm bcrypt, không bao giờ lưu bản gốc |
| `full_name` | ✔ | 1–100 ký tự |
| `phone` | ✔ | 8–15 chữ số, có thể bắt đầu bằng `+`; dấu cách/gạch ngang được tự bỏ; không được trùng |
| `marketing_consent` | | Đồng ý nhận email/tin nhắn ưu đãi – mặc định `false` (không tick) |
| `role` | | `customer` (mặc định) hoặc `driver` |

- Gửi `role: "admin"` hoặc thêm trường lạ (vd. `is_active`) → bị từ chối.
- **Tài khoản admin không đăng ký qua API**, chỉ được tạo trực tiếp trong database.

**Kết quả:**

| Mã | Ý nghĩa |
|---|---|
| `201` | Tạo thành công – trả về thông tin user (không bao giờ có mật khẩu). Frontend chuyển sang trang đăng nhập |
| `409` | `Ten dang nhap da duoc su dung` / `Email da duoc su dung` / `So dien thoai da duoc su dung` |
| `422` | Dữ liệu không hợp lệ hoặc thiếu trường – xem `detail` để biết trường nào sai |

**Đối chiếu Acceptance Criteria (user story Đăng ký):**

| Acceptance Criteria | Làm ở đâu |
|---|---|
| Mọi trường bắt buộc, email và số điện thoại đúng định dạng | Backend (bảng trên) + frontend |
| Email đã đăng ký bị từ chối kèm thông báo | Backend – `409` |
| Mật khẩu ≥ 12 ký tự, kiểm tra cả ở server và trình duyệt, lưu dạng băm | Backend kiểm tra + bcrypt; frontend kiểm tra thêm |
| Thành công thì chuyển sang trang đăng nhập | Frontend (khi nhận `201`) |
| Ô đồng ý marketing không bắt buộc, mặc định không tick | Backend – `marketing_consent` mặc định `false`; frontend để ô không tick |
| Link tới privacy notice ngắn | Frontend |

### `POST /api/v1/auth/login` – Đăng nhập

Đăng nhập bằng **email hoặc tên đăng nhập** (cùng một ô `login`) + mật khẩu.
Có ký tự `@` → tìm theo email, không có → tìm theo username. Không phân biệt hoa thường.
Mật khẩu được giữ **nguyên từng ký tự** (kể cả khoảng trắng) để password manager và dán mật khẩu hoạt động đúng.

**Body:**

```json
{
  "login": "an.nguyen",
  "password": "matkhau12345"
}
```

**Kết quả `200`:** body chứa thông tin user, **session ID chỉ nằm trong cookie**:

```
Set-Cookie: session_id=kX9f2...; HttpOnly; Path=/; SameSite=lax; Secure
Cache-Control: no-store
```

```json
{
  "user": {
    "id": "9183886b-...",
    "username": "an.nguyen",
    "email": "an.nguyen@example.com",
    "full_name": "Nguyen Van An",
    "phone": "0901234567",
    "role": "customer",
    "is_active": true,
    "marketing_consent": false,
    "created_at": "2026-11-07T13:56:00+07:00"
  }
}
```

| Mã | Ý nghĩa |
|---|---|
| `200` | Đúng thông tin – tạo phiên mới, gửi cookie `session_id` |
| `401` | `Thong tin dang nhap khong dung` – sai email/username **hoặc** mật khẩu (không nói trường nào sai) |
| `403` | `Tai khoan da bi khoa` – mật khẩu đúng nhưng `is_active = false` |
| `422` | Thiếu trường hoặc có trường lạ |
| `429` | `Dang nhap sai qua nhieu lan, thu lai sau 15 phut` – sai 5 lần trong 15 phút, tài khoản bị khoá 15 phút (kể cả nhập đúng) |

### `GET /api/v1/auth/me` – Ai đang đăng nhập

Không có body – trình duyệt **tự gửi cookie**. Trả `200` thông tin user, hoặc `401 "Chua dang nhap hoac phien da het han"`.
Dashboard gọi API này **mỗi khi trang hiện ra** (kể cả khi bấm Back); nhận `401` thì chuyển về trang đăng nhập.

### `POST /api/v1/auth/logout` – Đăng xuất

Không có body. **Xoá phiên ở server** và xoá cookie, luôn trả `204 No Content` (kể cả khi chưa đăng nhập).
Sau đó `/me` và mọi API cần đăng nhập trả `401` – kể cả khi ai đó đã chép được session ID cũ.

### Phiên đăng nhập hoạt động thế nào

```
ĐĂNG NHẬP  /login đúng → tạo session ID ngẫu nhiên MỚI → lưu bảng sessions → gửi cookie session_id
DÙNG       trình duyệt tự gửi cookie ở mọi request (JavaScript không đọc được – HttpOnly)
           → server tìm session ID → còn trong 30 phút không hoạt động? → cho qua + gia hạn 30 phút
           → không thấy / quá 30 phút → 401
ĐĂNG XUẤT  /logout → xoá dòng trong sessions + xoá cookie → mọi request sau đó 401
```

| Phiên bị xoá khi | Ghi chú |
|---|---|
| Đăng xuất | Chỉ phiên của trình duyệt đó – máy khác vẫn đăng nhập |
| 30 phút không hoạt động | Mỗi lần gọi API được gia hạn thêm 30 phút |
| Đăng nhập lại trên cùng trình duyệt | Phiên cũ bị xoá, cấp session ID mới |
| Xoá tài khoản | Database tự xoá (`ON DELETE CASCADE`) |
| Đổi mật khẩu / admin khoá | **Chưa làm** – đã có sẵn hàm `auth_service.delete_all_sessions(db, user_id)` |

> **Thử trên Swagger:** mở bằng `http://127.0.0.1:8000/docs` hoặc `http://localhost:8000/docs`
> (trình duyệt coi 2 địa chỉ này là an toàn nên nhận cookie `Secure`). Gọi `/login` xong thì `/me` và `/logout`
> tự có cookie – không cần bấm **Authorize**.

**Đối chiếu Acceptance Criteria (user story Đăng nhập):**

| Acceptance Criteria | Backend | Frontend |
|---|---|---|
| Email + mật khẩu đúng → mở dashboard khách hàng | `/login` trả `200` (nhận cả email lẫn username) | Chuyển sang dashboard |
| Sai thông tin báo lỗi, không nói trường nào sai | Cùng một thông báo `401` | Hiện thông báo |
| Đăng xuất kết thúc phiên, Back không mở lại dashboard | `/logout` xoá phiên; `Cache-Control: no-store`; `/me` trả `401` | Gọi `/me` mỗi khi dashboard hiện ra (cả sự kiện `pageshow`), `401` → về trang đăng nhập |
| Sai 5 lần trong 15 phút → khoá 15 phút | Đếm theo tài khoản, trả `429` | Hiện thông báo |
| Session ID mới khi đăng nhập, cookie HttpOnly + Secure, hết sau 30 phút không hoạt động | Đã làm | Không cần làm gì (trình duyệt tự lo cookie) |
| Password manager và dán mật khẩu dùng được | Không cắt khoảng trắng mật khẩu | Không chặn paste, ô mật khẩu có `autocomplete="current-password"` |

---

## 5. Database và migration

### Bảng `users`

| Cột | Kiểu | Ghi chú |
|---|---|---|
| `id` | UUID | Khoá chính |
| `username` | VARCHAR(30) | Unique, chữ thường – dùng để đăng nhập |
| `email` | VARCHAR(255) | Unique |
| `password_hash` | VARCHAR(255) | Mật khẩu đã mã hoá bcrypt (`$2b$12$...`) |
| `full_name` | VARCHAR(100) | |
| `phone` | VARCHAR(20) | Unique, bắt buộc |
| `role` | ENUM `customer` / `driver` / `admin` | Mặc định `customer` |
| `is_active` | BOOLEAN | Mặc định `true` |
| `marketing_consent` | BOOLEAN | Mặc định `false` |
| `failed_login_count` | INTEGER | Số lần đăng nhập sai trong cửa sổ 15 phút hiện tại |
| `failed_login_started_at` | TIMESTAMPTZ | Thời điểm lần sai đầu tiên của cửa sổ, NULL nếu chưa sai |
| `locked_until` | TIMESTAMPTZ | Bị khoá đến lúc nào, NULL nếu không bị khoá |
| `created_at`, `updated_at` | TIMESTAMPTZ | |

### Bảng `sessions` (phiên đăng nhập)

| Cột | Kiểu | Ghi chú |
|---|---|---|
| `id` | VARCHAR(64) | Khoá chính – chính là session ID trong cookie |
| `user_id` | UUID | FK → `users.id`, xoá user thì tự xoá phiên |
| `created_at` | TIMESTAMPTZ | Lúc đăng nhập |
| `last_seen_at` | TIMESTAMPTZ | Lần cuối dùng – quá 30 phút thì hết phiên |

### Xem nhanh bằng psql

```powershell
psql -h localhost -U privatehire -d privatehire
```

```sql
\dt                                   -- liệt kê bảng
\d users                              -- cấu trúc bảng users
SELECT email, full_name, phone, role, created_at FROM users;
\q                                    -- thoát
```

### Thay đổi cấu trúc database (migration)

Sau khi sửa model trong `app\models\` (trong thư mục `backend\`):

```powershell
.venv\Scripts\alembic revision --autogenerate -m "mo ta thay doi"
# kiểm tra file mới trong alembic\versions\ rồi:
.venv\Scripts\alembic upgrade head
```

Docker tự áp dụng migration mới khi build lại – không cần làm gì thêm.

---

## 6. Xem dữ liệu bằng pgAdmin 4

pgAdmin 4 đã có sẵn nếu lúc cài PostgreSQL bạn giữ thành phần này (tìm **pgAdmin 4** trong Start Menu).
Chưa có thì `winget install PostgreSQL.pgAdmin`. Lần đầu mở có thể bị hỏi **master password** – đặt gì cũng được nhưng phải nhớ.

### 6.1. Kết nối

Chuột phải **Servers** → **Register** → **Server...**, rồi điền:

| Ô | Database trên máy (Cách A) | Database trong Docker (Cách B) |
|---|---|---|
| General → Name | `PrivateHire` | `PrivateHire (Docker)` |
| Connection → Host | `localhost` | `localhost` |
| Port | `5432` | `5433` |
| Maintenance database | `privatehire` | `privatehire` |
| Username | `privatehire` | `privatehire` |
| Password | mật khẩu trong `backend\.env` | `POSTGRES_PASSWORD` trong `.env` gốc |

> Server **PostgreSQL 18** do bộ cài tạo sẵn (user `postgres`) cũng xem được, nhưng nên dùng server riêng như trên.

### 6.2. Xem dữ liệu

Mở `Servers → PrivateHire → Databases → privatehire → Schemas → public → Tables → users`,
chuột phải **users** → **View/Edit Data** → **All Rows**.

- Dữ liệu không tự cập nhật → bấm **F5**.
- Chạy SQL: chuột phải database **privatehire** → **Query Tool**, gõ câu lệnh, bấm **F5**.

```sql
SELECT email, full_name, phone, role, created_at FROM users ORDER BY created_at DESC;
SELECT role, count(*) FROM users GROUP BY role;
```

### 6.3. Lưu ý an toàn

- **Không sửa tay `password_hash`** – sửa sai thì user đó không đăng nhập được nữa.
- Sửa ô trong **View/Edit Data** phải bấm **Save Data Changes** (F6) mới ghi – lỡ sửa nhầm thì đóng tab, đừng lưu.
- **Không** Delete/Drop bảng, **không** thêm/sửa cột bằng pgAdmin – mọi thay đổi cấu trúc đi qua migration (mục 5).

---

## 7. Cấu trúc thư mục

```
COMP1807_PrivateHire/
├── .env                      # (tự tạo) mật khẩu cho Docker – Cách B
├── .env.example              # mẫu của .env gốc
├── .gitattributes            # giữ *.sh ở dạng LF để chạy được trong container
├── .gitignore
├── docker-compose.yml        # khai báo 2 service: db (postgres:18) + backend
├── README.md
└── backend/
    ├── .env                  # (tự tạo) kết nối database trên máy – Cách A
    ├── .env.example          # mẫu của backend\.env
    ├── .gitignore
    ├── .dockerignore         # loại .env, .venv, tests khỏi image Docker
    ├── Dockerfile            # đóng gói backend (python:3.13-slim, user thường)
    ├── docker-entrypoint.sh  # trong Docker: chạy migration rồi bật server
    ├── requirements.txt      # thư viện để chạy
    ├── requirements-dev.txt  # + thư viện test
    ├── alembic.ini
    ├── alembic/versions/     # các file migration
    ├── tests/                # test (pytest)
    └── app/
        ├── main.py           # tạo app FastAPI, gắn router
        ├── core/config.py    # đọc cấu hình từ .env
        ├── core/security.py  # hash / kiểm tra mật khẩu
        ├── db/base.py        # Base của SQLAlchemy
        ├── db/session.py     # kết nối database, get_db()
        ├── models/user.py    # bảng users, UserRole
        ├── models/session.py # bảng sessions (UserSession)
        ├── schemas/user.py   # kiểm tra dữ liệu vào/ra (RegisterIn, UserOut)
        ├── schemas/auth.py   # LoginIn, LoginOut
        ├── services/user_service.py  # logic đăng ký
        ├── services/auth_service.py  # đăng nhập, khoá tài khoản, tạo/kiểm tra/xoá phiên
        ├── api/deps.py       # get_current_user: đọc cookie session_id
        └── api/v1/auth.py    # endpoint /auth/register, /login, /me, /logout
```

---

## 8. Lỗi thường gặp

### Cài đặt

| Lỗi | Cách xử lý |
|---|---|
| `'python' is not recognized` / mở Microsoft Store | Cài Python từ python.org, tick **Add python.exe to PATH**. Hoặc dùng `py` thay `python` |
| `'psql' is not recognized` | Chưa thêm `C:\Program Files\PostgreSQL\<phiên bản>\bin` vào PATH (bước 1.1), hoặc chưa mở lại PowerShell |
| `running scripts is disabled on this system` | Chỉ gặp khi chạy `Activate.ps1` → `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, hoặc bỏ qua kích hoạt |
| `Start-Service: Cannot find any service` | Chưa cài PostgreSQL |
| `Start-Service: Cannot open ... service` | PowerShell không có quyền Admin. Nếu `Get-Service` đã báo `Running` thì không cần chạy lệnh này |

### Database (Cách A)

| Lỗi | Cách xử lý |
|---|---|
| `DATABASE_URL Field required` | Chưa có `backend\.env` → bước 1.4 |
| `password authentication failed for user "privatehire"` | Mật khẩu trong `backend\.env` không khớp → `psql -U postgres -c "ALTER ROLE privatehire PASSWORD 'moi';"` rồi sửa `.env` |
| `password authentication failed for user "postgres"` | Sai mật khẩu quản trị đặt lúc cài PostgreSQL |
| `connection refused` | PostgreSQL chưa chạy → `Get-Service postgresql*` |
| `role "<tên máy>" does not exist` | Gõ `psql` thiếu `-U privatehire -h localhost` |
| Không thấy bảng `users` | Chưa chạy `alembic upgrade head`, hoặc đang mở nhầm database |
| `privatehire_test` không có bảng | Bình thường – test tự xoá bảng sau khi chạy |
| Swagger trả `422` | Dữ liệu gửi lên sai quy tắc – đọc `msg` trong Response body |

### Đăng nhập (khi thử tay)

| Lỗi | Cách xử lý |
|---|---|
| `429 Dang nhap sai qua nhieu lan` | Chờ 15 phút, hoặc mở khoá tay: `psql -U privatehire -h localhost -d privatehire -c "UPDATE users SET locked_until = NULL, failed_login_count = 0;"` |
| Đăng nhập xong mà `/me` vẫn `401` trên Swagger | Mở Swagger bằng `127.0.0.1` hoặc `localhost` (không dùng IP mạng LAN) – cookie `Secure` chỉ được gửi trên địa chỉ an toàn |
| `/me` trả `401` sau một lúc không dùng | Bình thường – phiên hết sau 30 phút không hoạt động, đăng nhập lại |

### Docker (Cách B)

| Lỗi | Cách xử lý |
|---|---|
| `failed to connect to the docker API ... dockerDesktopLinuxEngine` | Docker Desktop chưa chạy → mở nó, chờ **Engine running** |
| `required variable POSTGRES_PASSWORD is missing a value` | Chưa có `.env` ở **thư mục gốc** (không phải `backend\.env`) → bước 2.1 |
| Không thấy container trong Docker Desktop | Lệnh `docker compose up` trước đó bị lỗi → đọc lỗi, sửa, chạy lại |
| Backend dừng ngay, log báo lỗi ở migration `0002` (`column "username" ... contains null values`) | Database Docker còn user tạo trước khi có username. Xoá dữ liệu Docker: `docker compose down -v` rồi `docker compose up -d --build` |
| `port is already allocated` | Cổng 8080/5433 đang bị dùng → đổi `BACKEND_PORT` / `DB_PORT` trong `.env` gốc |
| Backend dừng ngay, log báo `exec ./docker-entrypoint.sh: no such file or directory` | File `.sh` bị đổi sang CRLF. Ở thư mục gốc: `Remove-Item backend\docker-entrypoint.sh; git checkout -- backend/docker-entrypoint.sh` rồi build lại |
| Backend báo `password authentication failed` | Đổi `POSTGRES_PASSWORD` sau khi volume đã tạo (Postgres chỉ đặt mật khẩu lần đầu). Đổi lại mật khẩu cũ, hoặc `docker compose down -v` (mất dữ liệu Docker) |
