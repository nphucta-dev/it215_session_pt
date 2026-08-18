# Phân quyền hệ thống thi trực tuyến — Dependency vs Middleware

## Phần A. Phân tích Input/Output

| Mục | Nội dung |
|---|---|
| Dữ liệu có trong JWT | `sub` (username), `role` (admin/user), `iat`, `exp` |
| Dữ liệu cần lấy từ hệ thống | Bản ghi user (để login/cấp token), danh sách exam, kết quả thi theo username |
| Thông tin request dùng để phân quyền | Method + path (để biết route nào cần role gì), `Authorization` header, path parameter (`exam_id`, `username`) để so quyền sở hữu |
| Kết quả khi được phép truy cập | 200/201 kèm `build_response()` chuẩn 6 trường (statusCode, data, message, timestamp, path, error=null) |
| Kết quả khi token/quyền không hợp lệ | Không có token hoặc token sai/hết hạn → 401; có token hợp lệ nhưng sai role hoặc không sở hữu dữ liệu → 403 |

## Phần B. Ba giải pháp

- **Giải pháp 1 — Dependency tại endpoint**: mỗi route khai báo `Depends(require_role(...))`. Rõ ràng, đọc là biết ngay quyền của route, tận dụng path parameter thật của FastAPI (không bị Bẫy 1). Nhược điểm: dễ quên gắn (Bẫy 3), dễ trùng lặp logic decode token.
- **Giải pháp 2 — Middleware theo bảng `PROTECTED_ROUTES`**: một chỗ quản lý tập trung, khó bỏ sót vì middleware chặn hết. Nhược điểm: phải tự so khớp path có tham số động (Bẫy 1 dễ xảy ra), phải tự xử lý OPTIONS thủ công (Bẫy 2), không biết quyền sở hữu dữ liệu (Bẫy 4) vì middleware chạy trước khi FastAPI parse path parameter theo route.
- **Giải pháp 3 — Kết hợp (đã chọn)**: Middleware chỉ làm việc chung — giải mã JWT nếu có, bỏ qua OPTIONS, bỏ qua route công khai — và gắn user vào `request.state`. Dependency ở từng endpoint xử lý role + ownership, dùng đúng path parameter FastAPI đã parse sẵn. Middleware không cần bảng path->role nên tránh hẳn Bẫy 1.

## Phần C. So sánh

| Tiêu chí | Dependency | Middleware | Kết hợp |
|---|---|---|---|
| Dễ đọc code | Cao (thấy ngay ở route) | Thấp (phải tra bảng riêng) | Cao |
| Khả năng tái sử dụng | Tốt (hàm `require_role` dùng lại) | Tốt (một nơi duy nhất) | Tốt nhất |
| Nguy cơ bỏ sót phân quyền | Cao (quên `Depends`) | Thấp (chặn tập trung) | Trung bình (vẫn cần gắn Depends nhưng có review dễ hơn) |
| Xử lý path parameter | Chính xác (FastAPI tự parse) | Rủi ro cao nếu so khớp chuỗi | Chính xác |
| Xử lý CORS preflight | Không liên quan (route không chạy) | Phải code thủ công bỏ qua OPTIONS | Middleware bỏ qua OPTIONS sẵn |
| Kiểm tra quyền sở hữu dữ liệu | Làm được (có path param) | Không làm được ở middleware | Làm được (ở Dependency) |
| Khả năng kiểm thử | Cao (test riêng từng dependency) | Trung bình (phải test qua middleware) | Cao |
| Khả năng bảo trì | Trung bình (rải rác nhiều route) | Cao (một bảng duy nhất) — nhưng dễ sai khi API đổi path | Cao |
| Hiệu năng | Tốt | Tốt (một lần decode) | Tốt (decode 1 lần ở middleware, dependency chỉ so sánh string/role) |

**Lựa chọn**: Giải pháp kết hợp (3) — vì nó tách đúng trách nhiệm: middleware lo phần chung (giải mã token, CORS, public route) không cần biết cấu trúc route; dependency lo phần nghiệp vụ cụ thể (role, ownership) với dữ liệu path parameter chính xác từ FastAPI, loại bỏ hoàn toàn rủi ro so khớp chuỗi của Bẫy 1.

**Khi không nên dùng giải pháp này**: hệ thống rất nhỏ (vài endpoint, một role duy nhất) thì thêm middleware là dư thừa — chỉ cần Dependency đơn giản. Ngược lại, hệ thống có hàng trăm route với quy tắc phân quyền đơn giản, đồng nhất (ví dụ chỉ cần "đăng nhập hay chưa") thì Middleware thuần theo bảng path có thể đủ và gọn hơn.

## Chạy thử

```bash
pip install -r requirements.txt
uvicorn main:app --reload
python -m pytest tests/test_auth.py -v
```

Tài khoản demo: `student01/pass123`, `student02/pass123` (role `user`), `admin01/admin123` (role `admin`).
