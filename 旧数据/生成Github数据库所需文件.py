import os, re, pandas as pd

def extract_codes(file_path):
    codes = set()
    for enc in ['utf-8-sig', 'gbk', 'utf-16', 'utf-8']:
        try:
            with open(file_path, 'r', encoding=enc, errors='ignore') as f:
                matches = re.findall(r'([a-zA-Z]{2,10})-?([0-9]{2,8})', f.read())
                for m in matches: codes.add(f"{m[0].upper()}-{m[1]}")
            if codes: break
        except: continue
    return codes

all_data = []
txt_files = [f for f in os.listdir('.') if f.lower().endswith('.txt') and '结果' not in f]
for fname in txt_files:
    for code in extract_codes(fname):
        all_data.append({"code": code, "source": fname})

df = pd.DataFrame(all_data)
# 汇总番号：同一番号合并来源，并计算重复次数
summary = df.groupby('code')['source'].apply(lambda x: ', '.join(sorted(set(x)))).reset_index()
# 增加一个标记位，方便网页高亮
summary['is_dup'] = summary['source'].apply(lambda x: 1 if ',' in x else 0)
summary.to_csv('db.csv', index=False, encoding='utf-8-sig')
print("数据库 db.csv 已生成")