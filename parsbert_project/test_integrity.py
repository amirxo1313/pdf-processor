#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت تست یکپارچگی - بررسی خروجی‌های تولید شده
"""

import json
import re
from pathlib import Path
from typing import List, Tuple, Dict


class IntegrityTester:
    """تست‌کننده یکپارچگی خروجی‌ها"""

    FORBIDDEN_KEYWORDS = [
        'lorem ipsum',
        'sample',
        'example',
        'placeholder',
        'dummy',
        'test',
        'نمونه',
        'تستی'
    ]

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.results = []

    def test_all_jsons(self) -> List[Dict]:
        """تست تمام فایل‌های JSON"""

        json_files = list(self.output_dir.glob('*_parsed.json'))

        print(f"🔍 در حال بررسی {len(json_files)} فایل JSON...\n")

        for json_file in json_files:
            result = self._test_single_file(json_file)
            self.results.append(result)

        self._print_summary()
        return self.results

    def _test_single_file(self, json_path: Path) -> Dict:
        """تست یک فایل"""

        result = {
            "file": json_path.name,
            "valid": True,
            "errors": [],
            "warnings": []
        }

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # تست 1: وجود فیلدهای ضروری
            required_fields = ['meta_data', 'title', 'body_text', 'paragraphs', 'entities', 'integrity_score']
            for field in required_fields:
                if field not in data:
                    result['errors'].append(f"فیلد {field} وجود ندارد")
                    result['valid'] = False

            # تست 2: بررسی محتوای جعلی
            body_text = data.get('body_text', '').lower()
            for keyword in self.FORBIDDEN_KEYWORDS:
                if keyword in body_text:
                    result['errors'].append(f"محتوای جعلی یافت شد: {keyword}")
                    result['valid'] = False

            # تست 3: بررسی پاراگراف‌های خالی
            paragraphs = data.get('paragraphs', [])
            empty_paras = [p for p in paragraphs if not p.get('text', '').strip()]
            if empty_paras:
                result['warnings'].append(f"{len(empty_paras)} پاراگراف خالی")

            # تست 4: بررسی integrity_score
            score = data.get('integrity_score', 0)
            if score < 0.85:
                result['warnings'].append(f"امتیاز یکپارچگی پایین: {score}")

            # تست 5: بررسی entities
            entities = data.get('entities', {})
            body_text_full = data.get('body_text', '')

            for entity_type, entity_list in entities.items():
                for entity in entity_list:
                    if entity and entity not in body_text_full:
                        result['errors'].append(f"Entity '{entity}' در متن وجود ندارد")
                        result['valid'] = False

            # تست 6: بررسی نرمال‌سازی فارسی
            if 'ي' in body_text or 'ك' in body_text:
                result['warnings'].append("حروف عربی نرمال‌سازی نشده")

        except json.JSONDecodeError:
            result['errors'].append("فرمت JSON نامعتبر است")
            result['valid'] = False
        except Exception as e:
            result['errors'].append(f"خطای غیرمنتظره: {e}")
            result['valid'] = False

        return result

    def _print_summary(self):
        """چاپ خلاصه نتایج"""

        print("\n" + "="*70)
        print("📊 خلاصه تست یکپارچگی")
        print("="*70)

        total = len(self.results)
        valid = sum(1 for r in self.results if r['valid'])
        invalid = total - valid

        print(f"✅ معتبر: {valid}/{total}")
        print(f"❌ نامعتبر: {invalid}/{total}")
        print("")

        # فایل‌های نامعتبر
        if invalid > 0:
            print("🚨 فایل‌های نامعتبر:")
            for r in self.results:
                if not r['valid']:
                    print(f"   - {r['file']}")
                    for error in r['errors']:
                        print(f"      ❌ {error}")

        # هشدارها
        warnings_count = sum(len(r['warnings']) for r in self.results)
        if warnings_count > 0:
            print(f"\n⚠️  کل هشدارها: {warnings_count}")

        print("="*70)


def main():
    tester = IntegrityTester("/home/amirxo/Desktop/pdf/output_json")
    results = tester.test_all_jsons()

    # ذخیره گزارش
    report_path = Path("/home/amirxo/Desktop/pdf/logs/integrity_test_report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n📄 گزارش کامل در: {report_path}")


if __name__ == "__main__":
    main()

