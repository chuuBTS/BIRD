import os
import sqlite3
import csv
from typing import List, Dict, Tuple

def get_database_files(root_dir: str) -> List[str]:
    """
    获取所有SQLite数据库文件的路径
    """
    sqlite_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.sqlite') or file.endswith('.db'):
                sqlite_files.append(os.path.join(root, file))
    return sqlite_files

def get_table_info(db_path: str) -> List[Dict]:
    """
    获取数据库中所有表的详细信息
    
    返回：包含每个表信息的字典列表，每个字典包含：
    - database_name: 数据库名称
    - table_name: 表名
    - row_count: 行数
    - column_count: 列数
    - column_names: 列名列表
    """
    database_name = os.path.splitext(os.path.basename(db_path))[0]
    tables_info = []
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for (table_name,) in tables:
            table_info = {
                'database_name': database_name,
                'table_name': table_name
            }
            
            # 获取列信息
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            table_info['column_count'] = len(columns)
            table_info['column_names'] = [col[1] for col in columns]  # col[1] 是列名
            
            # 获取行数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            table_info['row_count'] = row_count
            
            tables_info.append(table_info)
            
        conn.close()
        
    except Exception as e:
        print(f"处理数据库 {db_path} 时出错: {str(e)}")
    
    return tables_info

def write_csv_report(tables_info: List[Dict], output_file: str) -> None:
    """
    将表信息写入CSV文件
    """
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # 写入表头
        writer.writerow(['Database', 'Table', 'Rows', 'Columns', 'Column Names'])
        
        # 写入数据
        for info in tables_info:
            writer.writerow([
                info['database_name'],
                info['table_name'],
                info['row_count'],
                info['column_count'],
                ', '.join(info['column_names'])
            ])

def main():
    """
    主函数
    """
    # 设置数据库根目录
    root_dir = "dev_20240627"
    output_file = "database_tables_stats.csv"
    
    # 获取所有数据库文件
    db_files = get_database_files(root_dir)
    print(f"发现 {len(db_files)} 个数据库文件")
    
    # 收集所有表的信息
    all_tables_info = []
    for db_file in db_files:
        print(f"\n处理数据库: {db_file}")
        tables_info = get_table_info(db_file)
        all_tables_info.extend(tables_info)
    
    # 生成CSV报告
    write_csv_report(all_tables_info, output_file)
    print(f"\n统计结果已保存到 {output_file}")

if __name__ == "__main__":
    main()