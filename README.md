# Cửa hàng hoa 20/10 — video demo gameplay

Bốn clip mô phỏng luật chơi của mini game sự kiện 20/10, dùng để cùng duyệt ý tưởng trước khi phát triển.

> **Đây là video mô phỏng, không phải quay game thật.** Script Python dựng kịch bản bấm nút của người chơi, vẽ từng khung hình bằng Pillow rồi ghép thành MP4 bằng ffmpeg. Mọi con số (thời lượng, điểm, mức phạt, mốc tối đa) chỉ để minh họa và sẽ chốt sau playtest.

## Video

| Vòng | File | Thời lượng | Nội dung |
|---|---|---|---|
| 1 — Trồng cây | [videos/Demo_Vong1_TrongCay.mp4](videos/Demo_Vong1_TrongCay.mp4) | 1:06 | A lên/xuống, B trái/phải, C chọn dụng cụ và xác nhận; có một lần chọn sai bị khóa 1,5s |
| 2 — Bê cây | [videos/Demo_Vong2_BeCay.mp4](videos/Demo_Vong2_BeCay.mp4) | 0:46 | Ba người cùng bê một chậu; đứng xa nhau quá thì chậu rơi, phải hốt đất và bị phạt thời gian |
| 3 — Chở cây | [videos/Demo_Vong3_ChoCay.mp4](videos/Demo_Vong3_ChoCay.mp4) | 0:48 | A giữ để rẽ trái, B giữ để rẽ phải, C giữ ga; có một lần va chạm |
| 4 — Làm biển hiệu | [videos/Demo_Vong4_LamBienHieu.mp4](videos/Demo_Vong4_LamBienHieu.mp4) | 1:07 | Hai người vẽ, tranh ghép xen kẽ 16 ô, người thứ ba đoán; ra tên "Sen Hớn Hở Bánh Mì" |

## Dựng lại video

Cần Windows, vì script dùng font Segoe UI và Segoe UI Emoji trong `C:/Windows/Fonts`.

```bash
pip install -r requirements.txt
cd scripts
python demo_vong1.py ../videos/Demo_Vong1_TrongCay.mp4
python demo_vong2.py ../videos/Demo_Vong2_BeCay.mp4
python demo_vong3.py ../videos/Demo_Vong3_ChoCay.mp4
python demo_vong4.py ../videos/Demo_Vong4_LamBienHieu.mp4
```

Mỗi clip mất khoảng 3–8 phút. Muốn xem nhanh vài khung hình mà không xuất video (Vòng 2–4), đặt biến `PREVIEW` là danh sách giây cần chụp:

```bash
PREVIEW="20,30" python demo_vong2.py preview.mp4   # tạo preview_20.png, preview_30.png
```

| File | Vai trò |
|---|---|
| `demo_vong1.py` | Vòng 1, đồng thời chứa các hàm vẽ cơ bản (font, emoji, nút, màu) |
| `demo_common.py` | Phần dùng chung cho Vòng 2–4: header, khung điện thoại, màn tiêu đề, bảng kết quả, xuất video |
| `demo_vong2.py` … `demo_vong4.py` | Kịch bản và hình vẽ riêng của từng vòng |

Tham số chỉnh nhanh nằm ở đầu mỗi file, ví dụ `GAME_LEN`, `X_POINTS` (Vòng 1), `PAUSE`, `PENALTY` (Vòng 2), `D_TOTAL`, `VMAX` (Vòng 3), `TURNS` (Vòng 4).
