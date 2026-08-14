import sys

orig_path = r"C:/Users/mforce0087/workhub_roomsupport_android_qa_automation/data/testcases/ROOM_01_original.csv"
labeled_path = r"C:/Users/mforce0087/workhub_roomsupport_android_qa_automation/data/testcases/ROOM_02_labeled.csv"
data_path = r"C:/Users/mforce0087/workhub_roomsupport_android_qa_automation/data/testcases/ROOM_01_original.csv"

esc_marker = "\\" + "u"

for label, path in [("Downloads(元)", orig_path), ("data/templates(コピー元)", data_path), ("labeled(出力)", labeled_path)]:
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    esc_count = sum(1 for line in lines if esc_marker in line)
    print(f"[{label}] 行数={len(lines)}, unicode escape含む行数={esc_count}")
    # Show first escaped line
    for i, line in enumerate(lines):
        if esc_marker in line:
            print(f"  サンプル行{i+1}: {line[:250]}")
            break
    print()
