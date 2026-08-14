"""
CSVファイル内の \\uXXXX 形式のUnicodeエスケープシーケンスを
正しい日本語テキストにデコードして再出力する。

対象: ROOM_02_labeled.csv
出力: 同ファイルを上書き (UTF-8, BOMなし)
"""

import re
import sys

INPUT_FILE = r"C:/Users/mforce0087/workhub_roomsupport_android_qa_automation/data/testcases/ROOM_02_labeled.csv"
OUTPUT_FILE = INPUT_FILE  # 上書き

ESC_PATTERN = re.compile(r"\\u([0-9a-fA-F]{4})")


def decode_unicode_escapes(text):
    """Replace all \\uXXXX sequences with their actual Unicode characters."""
    return ESC_PATTERN.sub(lambda m: chr(int(m.group(1), 16)), text)


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    esc_marker = "\\" + "u"
    before_count = content.count(esc_marker)

    decoded = decode_unicode_escapes(content)

    after_count = decoded.count(esc_marker)

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        f.write(decoded)

    print(f"=== デコード完了 ===")
    print(f"ファイル: {OUTPUT_FILE}")
    print(f"デコード前 \\uXXXX 出現数: {before_count}")
    print(f"デコード後 \\uXXXX 出現数: {after_count}")
    print()

    # Verify sample
    lines = decoded.split("\n")
    sample_count = 0
    for i, line in enumerate(lines):
        if "steps_actions" in lines[0] and i > 0 and len(line) > 100:
            if sample_count < 3:
                # Find steps_actions content
                print(f"行{i+1} サンプル(先頭250文字):")
                print(f"  {line[:250]}")
                print()
                sample_count += 1


if __name__ == "__main__":
    main()
