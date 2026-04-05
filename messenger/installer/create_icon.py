"""Generate app icon for LAN Messenger (creates .ico file)."""

import struct
import zlib
import os


def create_simple_ico(output_path: str):
    """Create a simple chat bubble icon as .ico file.

    Generates a 32x32 icon with a yellow chat bubble on brown background,
    matching the KakaoTalk color scheme.
    """
    size = 32

    # Create pixel data (BGRA format, bottom-up)
    pixels = []
    for y_inv in range(size):
        y = size - 1 - y_inv  # ICO is bottom-up
        row = []
        for x in range(size):
            # Background: dark brown (#3C1E1E)
            bg = (0x1E, 0x1E, 0x3C, 0xFF)  # BGRA
            # Yellow bubble (#FEE500)
            bubble = (0x00, 0xE5, 0xFE, 0xFF)  # BGRA
            # White for text dots
            white = (0xFF, 0xFF, 0xFF, 0xFF)
            # Transparent
            transparent = (0x00, 0x00, 0x00, 0x00)

            # Round corners for background
            cx, cy = size // 2, size // 2
            dist_corner = max(abs(x - cx), abs(y - cy))

            if dist_corner > 14:
                row.extend(transparent)
                continue

            # Chat bubble shape (rounded rect with tail)
            bx, by = x - 5, y - 6
            bw, bh = 22, 16

            in_bubble = False
            if 0 <= bx < bw and 0 <= by < bh:
                # Rounded corners
                corner_r = 4
                if bx < corner_r and by < corner_r:
                    if (corner_r - bx) ** 2 + (corner_r - by) ** 2 <= corner_r ** 2:
                        in_bubble = True
                elif bx >= bw - corner_r and by < corner_r:
                    if (bx - (bw - corner_r - 1)) ** 2 + (corner_r - by) ** 2 <= corner_r ** 2:
                        in_bubble = True
                elif bx < corner_r and by >= bh - corner_r:
                    if (corner_r - bx) ** 2 + (by - (bh - corner_r - 1)) ** 2 <= corner_r ** 2:
                        in_bubble = True
                elif bx >= bw - corner_r and by >= bh - corner_r:
                    if (bx - (bw - corner_r - 1)) ** 2 + (by - (bh - corner_r - 1)) ** 2 <= corner_r ** 2:
                        in_bubble = True
                else:
                    in_bubble = True

            # Tail of bubble
            if 3 <= x <= 7 and 22 <= y <= 26:
                tail_offset = y - 22
                if x <= 7 - tail_offset:
                    in_bubble = True

            # Three dots inside bubble (text indicator)
            in_dot = False
            for dx in [11, 16, 21]:
                dot_dist = (x - dx) ** 2 + (y - 14) ** 2
                if dot_dist <= 4:
                    in_dot = True

            if in_dot and in_bubble:
                row.extend(white)
            elif in_bubble:
                row.extend(bubble)
            elif dist_corner <= 14:
                row.extend(bg)
            else:
                row.extend(transparent)

        pixels.extend(row)

    pixel_data = bytes(pixels)

    # Create PNG for ICO
    # BMP header for ICO entry
    bmp_header_size = 40
    bmp_data_size = size * size * 4  # BGRA
    mask_size = ((size + 31) // 32) * 4 * size  # AND mask

    # BITMAPINFOHEADER (height is doubled for ICO)
    bmp_header = struct.pack('<IiiHHIIiiII',
        bmp_header_size,    # biSize
        size,               # biWidth
        size * 2,           # biHeight (doubled for ICO)
        1,                  # biPlanes
        32,                 # biBitCount
        0,                  # biCompression
        bmp_data_size + mask_size,  # biSizeImage
        0,                  # biXPelsPerMeter
        0,                  # biYPelsPerMeter
        0,                  # biClrUsed
        0,                  # biClrImportant
    )

    # AND mask (all zeros = all opaque, but we use alpha channel)
    and_mask = b'\x00' * mask_size

    image_data = bmp_header + pixel_data + and_mask

    # ICO file header
    ico_header = struct.pack('<HHH', 0, 1, 1)  # reserved, type=ICO, count=1

    # ICO directory entry
    data_offset = 6 + 16  # header + 1 entry
    ico_entry = struct.pack('<BBBBHHII',
        size if size < 256 else 0,  # width
        size if size < 256 else 0,  # height
        0,    # color palette
        0,    # reserved
        1,    # color planes
        32,   # bits per pixel
        len(image_data),  # data size
        data_offset,      # data offset
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(ico_header)
        f.write(ico_entry)
        f.write(image_data)

    print(f"Icon created: {output_path}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    create_simple_ico(os.path.join(script_dir, "app_icon.ico"))
