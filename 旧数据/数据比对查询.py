import os
import re
import pandas as pd

def extract_codes(file_path):
    """保持上个版本运行良好的提取逻辑"""
    codes = set()
    encodings = ['utf-8-sig', 'gbk', 'utf-16', 'utf-8']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc, errors='ignore') as f:
                content = f.read()
                # 匹配：2-10位字母 + 可选横杠 + 2-8位数字
                matches = re.findall(r'([a-zA-Z]{2,10})-?([0-9]{2,8})', content)
                for m in matches:
                    codes.add(f"{m[0].upper()}-{m[1]}")
            if codes: break
        except:
            continue
    return codes

def run_compare():
    # 获取当前目录下所有txt
    txt_files = [f for f in os.listdir('.') if f.lower().endswith('.txt') and '结果' not in f]
    
    if not txt_files:
        print("未找到任何 .txt 文件，请检查路径。")
        return

    all_data = []
    # 遍历文件提取番号
    for fname in txt_files:
        print(f"正在读取: {fname}...")
        codes = extract_codes(fname)
        for code in codes:
            all_data.append({"番号": code, "隶属于哪份文件": fname})

    if not all_data:
        print("未能提取到有效数据。")
        return

    # 数据处理：按番号分组，合并文件名
    df = pd.DataFrame(all_data)
    # 核心：将同一个番号的来源合并到一起，并统计出现次数用于高亮判断
    summary = df.groupby('番号')['隶属于哪份文件'].apply(lambda x: ', '.join(sorted(set(x)))).reset_index()
    
    # 导出 Excel 并在导出前定义高亮样式
    output_file = '比对结果汇总_高亮去重版.xlsx'

    # 定义高亮函数
    def highlight_rows(row):
        # 如果来源文件名里包含逗号，说明在至少两份文件里出现了
        if ',' in str(row['隶属于哪份文件']):
            return ['background-color: #FFC7CE; color: #9C0006'] * len(row)
        return [''] * len(row)

    # 应用样式并保存
    try:
        styled_df = summary.style.apply(highlight_rows, axis=1)
        styled_df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"\n✅ 处理完成！请查看: {output_file}")
    except Exception as e:
        print(f"导出 Excel 样式失败（可能缺少 openpyxl 库），已保存为普通 CSV: {e}")
        summary.to_csv('比对结果_无高亮.csv', index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    run_compare()