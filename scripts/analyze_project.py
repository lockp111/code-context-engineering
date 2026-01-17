#!/usr/bin/env python3
"""
Code Context Analyzer - 项目静态分析工具

静态分析代码库，生成结构化的项目元数据，辅助 Agent 理解项目。
"""

import argparse
import sys
from pathlib import Path

# Add the scripts directory to path so we can import the analyzer package
sys.path.append(str(Path(__file__).parent))

from analyzer.engine import ProjectAnalyzer
from analyzer.formatter import to_markdown

def main():
    parser = argparse.ArgumentParser(description="项目代码静态分析工具")
    parser.add_argument("path", help="项目根目录路径")
    parser.add_argument("-o", "--output", help="输出文件路径 (默认: stdout)")
    parser.add_argument("--depth", type=int, default=10, help="最大扫描深度")
    parser.add_argument("--extensions", nargs="+", help="仅分析指定扩展名 (如 py js)")
    
    args = parser.parse_args()
    
    # 执行分析 (默认总是完整分析)
    analyzer = ProjectAnalyzer(
        project_path=args.path,
        max_depth=args.depth,
        extensions=args.extensions
    )
    
    try:
        result = analyzer.analyze()
    except Exception as e:
        print(f"❌ 分析失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # 格式化输出 (Markdown Only)
    output_content = to_markdown(result)
    
    # 输出结果
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output_content, encoding='utf-8')
        print(f"✅ 已保存到: {out_path}", file=sys.stderr)
    else:
        print(output_content)

if __name__ == "__main__":
    main()
