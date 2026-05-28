#!/usr/bin/env python3
"""
行业一页纸自动化生成脚本
使用 Alpha派 Agent Mode 11 批量生成各行业基本面研究文档
"""

import os
import sys
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from data.collectors.alpha_pai import AlphaPaiCollector
from research.industry_mapping import get_all_industries, get_commodities_by_industry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)
logger = logging.getLogger("industry_research")

# 输出目录
OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "commodity_chains"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 缓存有效期（天）
CACHE_DAYS = 7


def get_output_path(industry: str) -> Path:
    """获取行业文档输出路径"""
    safe_name = industry.replace("与", "_").replace("/", "_")
    return OUTPUT_DIR / f"industry_{safe_name}.md"


def is_fresh(path: Path, days: int = CACHE_DAYS) -> bool:
    """检查文件是否在缓存有效期内"""
    if not path.exists():
        return False
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    return datetime.now() - mtime < timedelta(days=days)


def generate_industry_research(industry: str, collector: AlphaPaiCollector) -> str:
    """调用 Alpha派生成行业一页纸"""
    logger.info(f"开始生成 [{industry}] 行业一页纸...")
    try:
        content = collector.agent_industry_one_page(industry)
        logger.info(f"[{industry}] 生成完成，长度 {len(content)} 字符")
        return content
    except Exception as e:
        logger.error(f"[{industry}] 生成失败: {e}")
        raise


def save_industry_research(industry: str, content: str):
    """保存行业研究文档"""
    output_path = get_output_path(industry)
    commodities = get_commodities_by_industry(industry)
    
    header = f"""# {industry}行业一页纸

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> 数据来源: Alpha派 Agent Mode 11（行业一页纸）
> 覆盖期货品种: {', '.join(commodities) if commodities else '无直接对应'}

---

"""
    full_content = header + content
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_content)
    
    logger.info(f"已保存: {output_path}")
    return output_path


def run_generation(
    industries: list,
    dry_run: bool = False,
    force: bool = False,
):
    """执行生成流程"""
    collector = AlphaPaiCollector()
    
    total = len(industries)
    success = 0
    skipped = 0
    failed = 0
    
    for i, industry in enumerate(industries, 1):
        output_path = get_output_path(industry)
        
        # 检查缓存
        if not force and is_fresh(output_path):
            logger.info(f"[{i}/{total}] [{industry}] 缓存有效，跳过")
            skipped += 1
            continue
        
        if dry_run:
            logger.info(f"[{i}/{total}] [{industry}] 将生成 → {output_path} (dry-run)")
            continue
        
        try:
            content = generate_industry_research(industry, collector)
            save_industry_research(industry, content)
            success += 1
        except Exception as e:
            logger.error(f"[{i}/{total}] [{industry}] 失败: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("生成报告")
    print("=" * 60)
    print(f"总计: {total}")
    print(f"成功: {success}")
    print(f"跳过: {skipped}")
    print(f"失败: {failed}")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 60)
    
    return success, skipped, failed


def main():
    parser = argparse.ArgumentParser(description="生成行业一页纸研究文档")
    parser.add_argument("--industry", help="指定单个行业生成（如'钢铁'）")
    parser.add_argument("--all", action="store_true", help="生成所有行业")
    parser.add_argument("--update", action="store_true", help="只更新过期/缺失的行业（默认）")
    parser.add_argument("--force", action="store_true", help="强制重新生成，忽略缓存")
    parser.add_argument("--dry-run", action="store_true", help="预览将要生成的行业，不实际调用")
    parser.add_argument("--list", action="store_true", help="列出所有可生成的行业")
    
    args = parser.parse_args()
    
    all_industries = get_all_industries()
    
    if args.list:
        print("可生成的行业列表:")
        for industry in all_industries:
            commodities = get_commodities_by_industry(industry)
            status = "✅" if is_fresh(get_output_path(industry)) else "⏳"
            print(f"  {status} {industry} ({len(commodities)}个品种)")
        return
    
    if args.industry:
        industries = [args.industry]
    elif args.all:
        industries = all_industries
    elif args.update:
        # 只生成过期或缺失的
        industries = [
            ind for ind in all_industries
            if not is_fresh(get_output_path(ind))
        ]
        logger.info(f"检测到 {len(industries)} 个需要更新的行业")
    else:
        # 默认：列出将要生成的行业，提示用户
        print("请指定操作模式:")
        print(f"  --all      生成所有 {len(all_industries)} 个行业")
        print(f"  --update   只更新过期/缺失的行业")
        print(f"  --industry 生成指定行业")
        print(f"  --list     列出所有行业")
        print(f"  --dry-run  预览模式")
        return
    
    run_generation(industries, dry_run=args.dry_run, force=args.force)


if __name__ == "__main__":
    main()
