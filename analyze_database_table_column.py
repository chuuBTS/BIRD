import os
import sqlite3
import plotly.graph_objects as go
from collections import defaultdict
from typing import Dict, List

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

def get_column_stats(db_path: str) -> Dict[str, Dict[str, List[str]]]:
    """
    获取数据库中所有表的列信息
    
    返回：
    {
        表名: {
            'columns': [列名1, 列名2, ...],
            'count': 列数
        }
    }
    """
    table_stats = {}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for (table_name,) in tables:
            # 获取列信息
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            table_stats[table_name] = {
                'columns': [col[1] for col in columns],  # col[1] 是列名
                'count': len(columns)
            }
            
        conn.close()
        
    except Exception as e:
        print(f"处理数据库 {db_path} 时出错: {str(e)}")
        
    return table_stats

def analyze_columns(root_dir: str) -> Dict[int, int]:
    """
    分析所有数据库表的列数分布
    
    返回：列数分布字典 (键：列数，值：具有该列数的表的数量)
    """
    column_dist = defaultdict(int)
    
    db_files = get_database_files(root_dir)
    print(f"发现 {len(db_files)} 个数据库文件")
    
    for db_file in db_files:
        print(f"\n处理数据库: {db_file}")
        db_name = os.path.splitext(os.path.basename(db_file))[0]
        table_stats = get_column_stats(db_file)
        
        # 更新分布统计并打印信息
        for table_name, stats in table_stats.items():
            column_count = stats['count']
            column_dist[column_count] += 1
            print(f"数据库 {db_name}, 表 {table_name}: {column_count} 列")
            print(f"列名: {', '.join(stats['columns'])}")
    
    return dict(column_dist)

def plot_column_distribution(column_dist: Dict[int, int]) -> None:
    """
    使用plotly绘制列数分布图
    """
    # 创建图形
    fig = go.Figure()
    
    # 添加柱状图
    x = sorted(column_dist.keys())
    y = [column_dist[k] for k in x]
    
    fig.add_trace(
        go.Bar(
            x=x,
            y=y,
            text=y,
            textposition='auto',
        )
    )
    
    # 更新布局
    fig.update_layout(
        title={
            'text': "数据库表的列数分布",
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="列数",
        yaxis_title="表的数量",
        xaxis=dict(
            dtick=1,
            tickmode='linear',
            range=[min(x) - 0.5, max(x) + 0.5],
        ),
        bargap=0.2,
    )
    
    # 保存为HTML文件
    fig.write_html("column_distribution.html")
    print("\n列数分布图已保存为 column_distribution.html")

def print_distribution(dist: Dict[int, int]) -> None:
    """
    打印分布信息
    """
    print("\n列数分布:")
    print("-" * 40)
    for k in sorted(dist.keys()):
        print(f"{k} 列的表数量: {dist[k]}")

def main():
    """
    主函数
    """
    # 设置数据库根目录
    # root_dir = "dev_20240627"
    root_dir = "train"
    
    # 分析列数统计
    column_dist = analyze_columns(root_dir)
    
    # 打印分布
    print_distribution(column_dist)
    
    # 绘制分布图
    plot_column_distribution(column_dist)

if __name__ == "__main__":
    main()

