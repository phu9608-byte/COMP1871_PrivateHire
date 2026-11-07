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

---

## 1. Cài đặt lần đầu

Tất cả lệnh bên dưới chạy trong thư mục `backend/`.

### 1.1. Cài thư viện Python

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt   # gồm cả pytest để chạy test
```

> `requirements.txt` chỉ chứa thư viện cần để chạy (dùng trong Docker). `requirements-dev.txt` thêm thư viện test.

> Muốn chạy bằng Docker thay vì cài tay? Xem [mục 3](#3-chạy-bằng-docker).

### 1.2. Tạo tài khoản và database trong PostgreSQL

Đảm bảo Postgres đang chạy:

```bash
sudo systemctl start postgresql
```

Vào Postgres bằng tài khoản quản trị:

```bash
sudo -u postgres psql
```

Tại dấu nhắc `postgres=#`, chạy (thay `MAT_KHAU_CUA_BAN` bằng mật khẩu bạn chọn):

```sql
CREATE ROLE privatehire LOGIN PASSWORD 'MAT_KHAU_CUA_BAN';
CREATE DATABASE privatehire OWNER privatehire;
CREATE DATABASE privatehire_test OWNER privatehire;
\q
```

> - Lệnh SQL phải kết thúc bằng dấu `;`. Lệnh của psql bắt đầu bằng dấu gạch chéo ngược `\` (không phải `/`).
> - Nếu dấu nhắc đổi thành `postgres-#` nghĩa là đang có lệnh gõ dở → gõ `\r` để xoá.

### 1.3. Tạo file `.env` (nơi chứa mật khẩu)

```bash
cp .env.example .env
```

Mở `.env` và thay `DOI_MAT_KHAU` bằng mật khẩu đã đặt ở bước 1.2:

```env
DATABASE_URL=postgresql+psycopg://privatehire:MAT_KHAU_CUA_BAN@localhost:5432/privatehire
TEST_DATABASE_URL=postgresql+psycopg://privatehire:MAT_KHAU_CUA_BAN@localhost:5432/privatehire_test
```

> Nếu mật khẩu có ký tự đặc biệt `@ : / ? #` thì phải mã hoá trong URL (ví dụ `@` → `%40`).

### 1.4. Tạo bảng

```bash
.venv/bin/alembic upgrade head
```

---

## 2. Chạy

### Chạy server

```bash
.venv/bin/fastapi dev app/main.py
```

- Swagger (thử API trên trình duyệt): http://127.0.0.1:8000/docs
- Kiểm tra server: http://127.0.0.1:8000/health

### Chạy test

```bash
.venv/bin/pytest -v
```

Test chạy trên database **`privatehire_test`** – bảng sẽ bị xoá và tạo lại mỗi lần chạy, không ảnh hưởng dữ liệu trong `privatehire`.

---

## 3. Chạy bằng Docker

Cách này không cần cài Python hay Postgres trên máy – Docker chạy cả backend và database.
File `docker-compose.yml` nằm ở **thư mục gốc** của dự án (không phải `backend/`).

### 3.1. Lần đầu

```bash
cd ~/Documents/COMP1871_PrivateHire        # thư mục gốc
cp .env.example .env                        # rồi sửa POSTGRES_PASSWORD trong .env
docker compose up -d --build
```

> Mật khẩu trong `.env` gốc chỉ nên dùng chữ và số – ký tự đặc biệt sẽ làm hỏng `DATABASE_URL`.
> Có thể tạo mật khẩu ngẫu nhiên bằng: `python3 -c "import secrets; print(secrets.token_hex(16))"`

Khi container khởi động, backend tự chạy `alembic upgrade head` (tạo/cập nhật bảng) rồi mới bật server.

| Dịch vụ | Địa chỉ trên máy |
|---|---|
| Swagger | http://127.0.0.1:8080/docs |
| Backend API | http://127.0.0.1:8080/api/v1/... |
| PostgreSQL (Docker) | `localhost:5433` – user `privatehire`, mật khẩu = `POSTGRES_PASSWORD` trong `.env` gốc |

> Dùng cổng **8080** và **5433** để không đụng với server chạy tay (8000) và Postgres cài trên máy (5432).
> Muốn đổi thì sửa `BACKEND_PORT` / `DB_PORT` trong `.env` gốc.

### 3.2. Lệnh hay dùng

| Lệnh | Tác dụng |
|---|---|
| `docker compose up -d --build` | Build lại image (sau khi sửa code) và chạy nền |
| `docker compose ps` | Xem trạng thái các container |
| `docker compose logs -f backend` | Xem log backend (Ctrl+C để thoát) |
| `docker compose restart backend` | Khởi động lại backend |
| `docker compose down` | Tắt và xoá container (**dữ liệu vẫn còn** trong volume `pgdata`) |
| `docker compose down -v` | Tắt và **xoá luôn dữ liệu database** – cẩn thận! |
| `docker compose exec db psql -U privatehire -d privatehire` | Mở psql vào database trong Docker |

### 3.3. Hai database khác nhau

| | Chạy tay (mục 2) | Chạy bằng Docker |
|---|---|---|
| Cổng Postgres | 5432 | 5433 |
| Mật khẩu | `backend/.env` | `.env` ở thư mục gốc |
| Dữ liệu | Postgres cài trên máy | Volume Docker `pgdata` |

Hai database **độc lập** – tài khoản đăng ký ở bên này không xuất hiện bên kia.
Trong pgAdmin, muốn xem database của Docker thì đăng ký thêm một server với **Port `5433`** (xem mục 6.2).

### 3.4. File liên quan

| File | Vai trò |
|---|---|
| `docker-compose.yml` (gốc) | Khai báo 2 service `db` (postgres:18) và `backend` |
| `.env.example` (gốc) | Mẫu cấu hình Docker – copy thành `.env` |
| `backend/Dockerfile` | Đóng gói backend (python:3.13-slim, chạy bằng user thường) |
| `backend/docker-entrypoint.sh` | Chạy migration rồi bật server |
| `backend/.dockerignore` | Loại `.env`, `.venv`, `tests/` khỏi image |

---

## 4. API hiện có

### `POST /api/v1/auth/register` – Đăng ký tài khoản

**Body:**

```json
{
  "email": "an.nguyen@example.com",
  "password": "matkhau123",
  "full_name": "Nguyen Van An",
  "phone": "0901234567",
  "role": "customer"
}
```

| Trường | Bắt buộc | Quy tắc |
|---|---|---|
| `email` | ✔ | Đúng định dạng email, tự chuyển về chữ thường, không được trùng |
| `password` | ✔ | Từ 8 ký tự, tối đa 72 byte, có ít nhất 1 chữ cái và 1 chữ số |
| `full_name` | ✔ | 1–100 ký tự |
| `phone` | | 8–15 chữ số, có thể bắt đầu bằng `+`; dấu cách/gạch ngang được tự bỏ; không được trùng |
| `role` | | `customer` (mặc định) hoặc `driver` |

- Gửi `role: "admin"` hoặc thêm trường lạ (vd. `is_active`) → bị từ chối.
- **Tài khoản admin không đăng ký qua API**, chỉ được tạo trực tiếp trong database.

**Kết quả:**

| Mã | Ý nghĩa |
|---|---|
| `201` | Tạo thành công – trả về thông tin user (không bao giờ có mật khẩu) |
| `409` | Email hoặc số điện thoại đã được sử dụng |
| `422` | Dữ liệu không hợp lệ – xem `detail` để biết trường nào sai |

---

## 5. Database

### Bảng `users`

| Cột | Kiểu | Ghi chú |
|---|---|---|
| `id` | UUID | Khoá chính |
| `email` | VARCHAR(255) | Unique |
| `password_hash` | VARCHAR(255) | Mật khẩu đã mã hoá bcrypt (`$2b$12$...`) |
| `full_name` | VARCHAR(100) | |
| `phone` | VARCHAR(20) | Unique, có thể NULL |
| `role` | ENUM `customer` / `driver` / `admin` | Mặc định `customer` |
| `is_active` | BOOLEAN | Mặc định `true` |
| `created_at`, `updated_at` | TIMESTAMPTZ | |

### Xem dữ liệu

**Bằng psql:**

```bash
psql -h localhost -U privatehire -d privatehire
```

```sql
\dt                                   -- liệt kê bảng
\d users                              -- cấu trúc bảng users
SELECT email, full_name, phone, role, created_at FROM users;
\q                                    -- thoát
```

**Bằng pgAdmin 4:** xem hướng dẫn chi tiết ở [mục 6](#6-dùng-pgadmin-4).

### Thay đổi cấu trúc database (migration)

Sau khi sửa model trong `app/models/`:

```bash
.venv/bin/alembic revision --autogenerate -m "mo ta thay doi"
# kiểm tra lại file mới trong alembic/versions/ rồi:
.venv/bin/alembic upgrade head
```

---

## 6. Dùng pgAdmin 4

pgAdmin 4 là phần mềm có giao diện để xem và quản lý PostgreSQL (xem bảng như Excel, chạy câu SQL).

### 6.1. Cài đặt (Kali / Debian)

Kho phần mềm của Kali không có pgAdmin, cần thêm kho chính thức của pgAdmin (dùng bản `trixie`):

```bash
# 1. Thêm khoá xác thực của kho pgAdmin
curl -fsS https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo gpg --dearmor -o /usr/share/keyrings/packages-pgadmin-org.gpg

# 2. Thêm kho pgAdmin
echo "deb [signed-by=/usr/share/keyrings/packages-pgadmin-org.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/trixie pgadmin4 main" | sudo tee /etc/apt/sources.list.d/pgadmin4.list

# 3. Cài bản desktop
sudo apt update
sudo apt install pgadmin4-desktop
```

> Nếu báo `gpg: command not found` → `sudo apt install gnupg` rồi chạy lại.

Mở pgAdmin: gõ `pgadmin4` trong terminal hoặc tìm **pgAdmin 4** trong menu ứng dụng.
Lần đầu có thể bị hỏi **master password** – đây là mật khẩu riêng để pgAdmin khoá các mật khẩu nó lưu, đặt gì cũng được nhưng phải nhớ.

### 6.2. Kết nối tới database

1. Cột bên trái: chuột phải **Servers** → **Register** → **Server...**
2. Tab **General** → **Name**: `PrivateHire` (tên hiển thị, đặt tuỳ ý)
3. Tab **Connection**:

   | Ô | Giá trị |
   |---|---|
   | Host name/address | `localhost` |
   | Port | `5432` |
   | Maintenance database | `privatehire` |
   | Username | `privatehire` |
   | Password | mật khẩu trong file `.env` |
   | Save password? | Bật |

4. Bấm **Save**. Nếu kết nối thành công, server `PrivateHire` hiện ở cột trái.

> **Database chạy trong Docker:** đăng ký thêm một server khác (vd. tên `PrivateHire (Docker)`) với **Port `5433`**,
> Username `privatehire`, Password = `POSTGRES_PASSWORD` trong file `.env` ở thư mục gốc.

> Muốn xem cả database test thì không cần thêm server – `privatehire_test` nằm ngay trong mục **Databases** của cùng server (nhưng thường trống vì test tự xoá dữ liệu sau khi chạy).

### 6.3. Xem dữ liệu bảng `users`

Mở lần lượt ở cột bên trái:

```
Servers
└── PrivateHire
    └── Databases
        └── privatehire
            └── Schemas
                └── public
                    └── Tables
                        └── users   ← chuột phải
```

Chuột phải **users** → **View/Edit Data** → **All Rows**. Dữ liệu hiện dạng bảng.

- **Dữ liệu không tự cập nhật**: sau khi đăng ký thêm tài khoản trên Swagger, bấm nút **Refresh** (hoặc **F5**) trong pgAdmin để thấy dòng mới.
- Xem nhanh số dòng: chuột phải **users** → **Count Rows**.

### 6.4. Xem cấu trúc bảng

Chuột phải **users** → **Properties...** → tab **Columns** (các cột, kiểu dữ liệu) và **Constraints** (khoá chính, unique).
Hoặc mở **users → Columns** ngay ở cột bên trái.

### 6.5. Chạy câu SQL (Query Tool)

Chuột phải database **privatehire** → **Query Tool**, gõ câu lệnh rồi bấm **F5** (hoặc nút ▶):

```sql
-- Xem các cột chính
SELECT email, full_name, phone, role, created_at FROM users ORDER BY created_at DESC;

-- Chỉ xem tài xế
SELECT email, full_name FROM users WHERE role = 'driver';

-- Đếm số tài khoản theo vai trò
SELECT role, count(*) FROM users GROUP BY role;
```

> Bôi đen một câu rồi bấm F5 để chỉ chạy câu đó.

### 6.6. Lưu ý an toàn

- **Không sửa tay cột `password_hash`** – đây là mật khẩu đã mã hoá bcrypt (`$2b$12$...`), sửa sai thì user đó không đăng nhập được nữa.
- Ở chế độ **View/Edit Data**, sửa ô xong phải bấm **Save Data Changes** (F6) mới được ghi – nếu lỡ sửa nhầm, đừng bấm lưu, cứ đóng tab.
- Không dùng **Delete/Drop** trên bảng hoặc database. Cần làm lại bảng thì dùng Alembic (`alembic downgrade base` rồi `alembic upgrade head`).
- Không tạo/sửa cột bằng pgAdmin – mọi thay đổi cấu trúc phải đi qua migration (mục 5) để cả nhóm có cùng database.

### 6.7. Lỗi thường gặp trong pgAdmin

| Lỗi | Cách xử lý |
|---|---|
| `password authentication failed` | Sai mật khẩu – dùng đúng mật khẩu trong `.env`. Chuột phải server → **Properties** → **Connection** để sửa |
| `connection refused` / `could not connect to server` | Postgres chưa chạy → `sudo systemctl start postgresql` |
| Không thấy bảng `users` | Chưa chạy `alembic upgrade head`, hoặc đang mở nhầm database `postgres` thay vì `privatehire` |
| Không thấy dữ liệu mới | Bấm **Refresh** / **F5** |
| Quên master password | Trên màn hình hỏi master password chọn **Reset Master Password** (các mật khẩu server đã lưu sẽ phải nhập lại) |

---

## 7. Cấu trúc thư mục

```
backend/
├── app/
│   ├── main.py               # Tạo app FastAPI, gắn router
│   ├── core/
│   │   ├── config.py         # Đọc cấu hình từ .env
│   │   └── security.py       # Hash / kiểm tra mật khẩu
│   ├── db/
│   │   ├── base.py           # Base của SQLAlchemy
│   │   └── session.py        # Kết nối database, get_db()
│   ├── models/user.py        # Bảng users, UserRole
│   ├── schemas/user.py       # Kiểm tra dữ liệu vào/ra (RegisterIn, UserOut)
│   ├── services/
│   │   └── user_service.py   # Logic nghiệp vụ đăng ký
│   └── api/v1/auth.py        # Endpoint /auth/...
├── alembic/versions/         # Các file migration
├── tests/                    # Test (pytest)
├── Dockerfile                # Đóng gói backend thành image
├── docker-entrypoint.sh      # Chạy migration rồi bật server (trong Docker)
├── .dockerignore
├── .env.example              # Mẫu cấu hình – copy thành .env
├── requirements.txt          # Thư viện để chạy
└── requirements-dev.txt      # + thư viện test
```

---

## 8. Lỗi thường gặp

| Lỗi | Cách xử lý |
|---|---|
| `DATABASE_URL Field required` | Chưa tạo file `.env` → làm bước 1.3 |
| `password authentication failed for user "privatehire"` | Mật khẩu trong `.env` không khớp. Đổi lại: `sudo -u postgres psql -c "ALTER ROLE privatehire PASSWORD 'moi';"` |
| `connection refused` | Postgres chưa chạy → `sudo systemctl start postgresql` |
| `role "<tên máy>" does not exist` | Gõ `psql` thiếu `-U privatehire -h localhost` |
| `collation version mismatch` (cảnh báo khi vào psql) | Hệ điều hành vừa cập nhật glibc. Vào `sudo -u postgres psql` và chạy `ALTER DATABASE <tên_db> REFRESH COLLATION VERSION;` cho từng database bị báo |
| `port is already allocated` khi `docker compose up` | Cổng 8080/5433 đang bị chương trình khác dùng → đổi `BACKEND_PORT` / `DB_PORT` trong `.env` gốc |
| `permission denied ... docker.sock` | Chưa vào nhóm `docker` → `sudo usermod -aG docker $USER` rồi đăng xuất/đăng nhập lại |
| Backend Docker báo `password authentication failed` | Đã đổi `POSTGRES_PASSWORD` sau khi volume được tạo (Postgres chỉ đặt mật khẩu lần đầu). Hoặc đổi lại mật khẩu cũ, hoặc `docker compose down -v` để tạo lại (mất dữ liệu Docker) |
| Swagger trả `422` | Dữ liệu gửi lên sai quy tắc – đọc `msg` trong Response body |
