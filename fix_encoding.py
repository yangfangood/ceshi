import pathlib
import sys

def fix_encoding(filepath):
    try:
        # 尝试多种编码读取，但最终统一保存为 UTF-8 without BOM
        for enc in ['utf-8-sig', 'utf-8', 'gbk', 'latin-1']:
            try:
                content = pathlib.Path(filepath).read_text(encoding=enc)
                break
            except UnicodeDecodeError:
                continue
        # 写入 UTF-8 without BOM
        pathlib.Path(filepath).write_text(content, encoding='utf-8')
        print(f"Fixed: {filepath}")
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")

# 扫描所有 .py 文件
for py_file in pathlib.Path('.').rglob('*.py'):
    fix_encoding(py_file)