import os
import re
import pandas as pd
import csv

# ================= 配置区 =================
SCAN_PATHS = [
    r"E:\日本骑兵\#整理完成",
    r"F:\日本骑兵\#整理完成",
]
EXTERNAL_DATA_FOLDER = "#待处理外部数据"
VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.wmv', '.iso', '.mov', '.flv', '.vob', '.rmvb', '.ts', '.m2ts')
HISTORY_KEYWORD = "500条"
# ==========================================

def extract_code(text):
    text = re.sub(r'[\u4e00-\u9fa5]', ' ', text)
    match = re.search(r'([a-zA-Z]{2,10})-?([0-9]{2,8})', text)
    if match:
        return f"{match.group(1).upper()}-{match.group(2)}"
    return None

def get_dynamic_label(path):
    path = path.rstrip(r'\/')
    drive = os.path.splitdrive(path)[0].replace(':', '').upper()
    parts = path.split(os.sep)
    folder_name = parts[1] if len(parts) > 1 else "根目录"
    return f"{drive}盘{folder_name.replace('#', '')}"

def main():
    resource_map = {}
    history_label_clean = ""
    
    # 1. 扫描历史库
    for f in os.listdir('.'):
        if f.lower().endswith('.txt') and HISTORY_KEYWORD in f:
            history_label_clean = os.path.splitext(f)[0]
            with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                for line in file:
                    c = extract_code(line)
                    if c:
                        res = resource_map.setdefault(c, {'labels': set(), 'size_bytes': 0})
                        res['labels'].add(history_label_clean)

    # 2. 处理外部数据
    if os.path.exists(EXTERNAL_DATA_FOLDER):
        for f_name in os.listdir(EXTERNAL_DATA_FOLDER):
            if f_name.lower().endswith('.txt'):
                clean_name = os.path.splitext(f_name)[0]
                current_file_codes = set()
                with open(os.path.join(EXTERNAL_DATA_FOLDER, f_name), 'r', encoding='utf-8', errors='ignore') as file:
                    for line in file:
                        c = extract_code(line)
                        if c:
                            current_file_codes.add(c)
                            res = resource_map.setdefault(c, {'labels': set(), 'size_bytes': 0})
                            res['labels'].add(clean_name)
                if current_file_codes:
                    with open(f"{clean_name}.txt", 'w', encoding='utf-8-sig') as out:
                        out.write('\n'.join(sorted(list(current_file_codes))))

    # 3. 扫描物理硬盘
    for path in SCAN_PATHS:
        if not os.path.exists(path): continue
        clean_name = get_dynamic_label(path)
        current_disk_codes = set()
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.lower().endswith(VIDEO_EXTENSIONS):
                    c = extract_code(file)
                    if c:
                        full_path = os.path.join(root, file)
                        try: f_size = os.path.getsize(full_path)
                        except: f_size = 0
                        current_disk_codes.add(c)
                        res = resource_map.setdefault(c, {'labels': set(), 'size_bytes': 0})
                        res['labels'].add(clean_name)
                        res['size_bytes'] += f_size
        if current_disk_codes:
            with open(f"{clean_name}.txt", 'w', encoding='utf-8-sig') as out:
                out.write('\n'.join(sorted(list(current_disk_codes))))

    # 4. 构建汇总
    final_list = []
    for code, info in resource_map.items():
        reports = info['labels']
        is_dup = 1 if (history_label_clean in reports and len(reports - {history_label_clean}) > 0) else 0
        size_gb = round(info['size_bytes'] / (1024**3), 2)
        
        final_list.append({
            'code': code,
            'size': size_gb if size_gb > 0 else "-",
            'source': " | ".join(sorted(list(reports))),
            'is_dup': is_dup
        })

    # 5. 导出
    df = pd.DataFrame(final_list).sort_values('code')
    # 本地预览表
    df.rename(columns={'code':'番号','size':'大小(GB)','source':'隶属清单'}).to_excel("全部数据汇总比对.xlsx", index=False)
    # GitHub 数据库 (强制加引号保护，防止逗号干扰)
    df[['code', 'size', 'source', 'is_dup']].to_csv("db.csv", index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
    print("✅ Python 处理完成，db.csv 已生成。")

if __name__ == "__main__":
    main()