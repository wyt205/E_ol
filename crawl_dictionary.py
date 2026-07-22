#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dictionary.net 单词爬虫
爬取单词数据并生成SQL文件
python crawl_dictionary.py [页数] [起始页]
"""

import requests
from bs4 import BeautifulSoup
import sys
import re
from urllib.parse import urljoin
import time
from typing import Optional, List, Dict

# 请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

BASE_URL = 'https://www.dictionary.net/zh'
DICTIONARY_URL = 'https://www.dictionary.net/zh/dictionary'


class DictionaryCrawler:
    def __init__(self, max_pages: int = 100):
        self.max_pages = max_pages
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.visited_urls = set()
        self.skipped_spelling_errors = 0
        self.found_words = []

    def is_spelling_error(self, pos_element: Optional[BeautifulSoup]) -> bool:
        """检查是否是误拼的单词"""
        if pos_element is None:
            return False
        text = pos_element.get_text().strip()
        return text == '误拼' or text == '拼写错误'

    def extract_phonetic_from_detail(self, soup: BeautifulSoup) -> tuple:
        """从详情页提取音标（UK和US）"""
        # 在详情页中查找音标区域
        phonetic_area = soup.find('div', class_='pronunciation-section')
        if not phonetic_area:
            return None, None

        # 提取UK音标和URL
        uk_label = phonetic_area.find('span', class_='pronunciation-label', string='UK')
        uk_phonetic_elements = phonetic_area.find_all('span', class_='pronunciation-phonetic')

        uk_phonic = None
        uk_audio = None
        if uk_label and uk_phonetic_elements:
            uk_phonic = uk_phonetic_elements[0].get_text().strip()
            # 提取音频URL
            audio_btn = phonetic_area.find('button', class_='audio-btn')
            if audio_btn and audio_btn.get('data-audio-url'):
                uk_audio = audio_btn.get('data-audio-url')

        # 提取US音标和URL
        us_label = phonetic_area.find('span', class_='pronunciation-label', string='US')
        us_phonetic_elements = phonetic_area.find_all('span', class_='pronunciation-phonetic')

        us_phonic = None
        us_audio = None
        if us_label and len(us_phonetic_elements) > 1:
            us_phonic = us_phonetic_elements[1].get_text().strip()
            # 提取音频URL
            audio_btn = phonetic_area.find('button', class_='audio-btn')
            if audio_btn and audio_btn.get('data-audio-url'):
                us_audio = audio_btn.get('data-audio-url')

        return uk_phonic, us_phonic

    def extract_definition_from_detail(self, soup: BeautifulSoup) -> Optional[str]:
        """从详情页提取释义"""
        # 在详情页中查找第一个定义
        definition_text = soup.find('p', class_='definition-text')
        if definition_text:
            return definition_text.get_text().strip()
        return None

    def extract_examples_from_detail(self, soup: BeautifulSoup) -> List[str]:
        """从详情页提取例句（只返回第一个例句）"""
        # 在详情页中查找所有例句
        example_elements = soup.find_all('p', class_='example-text')
        if example_elements:
            # 只返回第一个例句
            first_example = example_elements[0].get_text().strip()
            return [first_example]
        return []

    def parse_word_page(self, word_url: str) -> Optional[Dict]:
        """解析单个单词详情页"""
        try:
            response = self.session.get(word_url, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取UK和US音标
            uk_phonic, us_phonic = self.extract_phonetic_from_detail(soup)

            # 提取释义
            definition = self.extract_definition_from_detail(soup)

            # 提取例句
            examples = self.extract_examples_from_detail(soup)

            # 从URL中提取单词
            word = word_url.split('/')[-1]

            print(f"    解析: {word}, uk_phonic={uk_phonic is not None}, us_phonic={us_phonic is not None}, examples={len(examples)}")

            # 检查是否有音标和例句
            if not uk_phonic and not us_phonic:
                print(f"    -> 返回None: 缺少音标")
                return None

            if not examples:
                print(f"    -> 返回None: 缺少例句")
                return None

            # 处理例句（格式："英文 中文"）
            processed_examples = []
            for example in examples:
                # 查找第一个双引号的位置
                first_quote = example.find('\"')
                if first_quote == -1:
                    print(f"    -> 跳过例句（无引号）: {example[:50]}...")
                    continue

                # 获取引号后的内容
                content = example[first_quote + 1:].strip()
                if not content:
                    continue

                # 查找中文字符的位置
                cn_start = 0
                for i, char in enumerate(content):
                    if '一' <= char <= '鿿':  # 中文字符范围
                        cn_start = i
                        break

                if cn_start > 0:
                    # 分割英文和中文
                    en = content[:cn_start].strip()
                    cn = content[cn_start:].strip()

                    # 去除最后的引号（如果有）
                    if cn.endswith('"'):
                        cn = cn[:-1].strip()
                    if cn.startswith('"'):
                        cn = cn[1:].strip()

                    processed_examples.append({'en': en, 'cn': cn})
                else:
                    print(f"    -> 跳过例句（无中文）: {example[:50]}...")

            if not processed_examples:
                print(f"    -> 返回None: 没有有效的例句")
                return None

            # 提取词性
            pos_element = soup.find('span', class_='pos-tag')
            pos = pos_element.get_text().strip() if pos_element else ''

            result = {
                'word': word,
                'pos': pos,
                'phonetic_uk': uk_phonic,
                'phonetic_us': us_phonic,
                'audio_url_uk': uk_phonic,  # 音频URL和音标路径一致
                'audio_url_us': us_phonic,
                'meaning': definition,
                'examples': processed_examples
            }
            print(f"    -> 成功解析: {word}")
            return result

        except Exception as e:
            print(f"解析 {word_url} 时出错: {e}")
            return None

    def crawl_dictionary_page(self, page: int) -> List[str]:
        """爬取词典索引页，获取所有单词链接"""
        url = f'{DICTIONARY_URL}?page={page}'
        print(f"\n正在爬取第 {page} 页: {url}")

        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找单词网格
            word_grid = soup.find('div', class_='word-grid')
            if not word_grid:
                print(f"第 {page} 页未找到单词网格")
                return []

            word_cards = word_grid.find_all('div', class_='word-card')
            print(f"第 {page} 页找到 {len(word_cards)} 个单词卡片")

            word_urls = []
            for i, card in enumerate(word_cards, 1):
                # 检查是否是误拼
                pos_element = card.find('span', class_='pos')
                if self.is_spelling_error(pos_element):
                    self.skipped_spelling_errors += 1
                    continue

                # 获取单词链接
                word_link = card.find('h3').find('a')
                if not word_link:
                    continue

                word_url = urljoin(BASE_URL, word_link['href'])
                word_urls.append(word_url)

            print(f"  第 {page} 页找到 {len(word_urls)} 个有效单词链接")
            return word_urls

        except Exception as e:
            print(f"\n爬取第 {page} 页时出错: {e}")
            return []

    def crawl_word_details(self, word_urls: List[str]) -> List[Dict]:
        """爬取单词详情页，提取详细信息"""
        results = []
        print(f"\n开始解析 {len(word_urls)} 个单词的详情页...")

        for i, word_url in enumerate(word_urls, 1):
            if word_url in self.visited_urls:
                continue

            self.visited_urls.add(word_url)
            word_name = word_url.split('/')[-1]
            print(f"  [{i}/{len(word_urls)}] 解析: {word_name}", end='\r')

            # 解析单词页面
            word_data = self.parse_word_page(word_url)
            if word_data:
                results.append(word_data)

        print(f"\n解析完成: 找到 {len(results)} 个有效单词")
        return results

    def generate_sql(self, output_file: str = 'words_insert.sql'):
        """生成SQL插入语句"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('-- Dictionary.net 单词数据\n')
            f.write('-- 自动生成时间: ' + time.strftime('%Y-%m-%d %H:%M:%S') + '\n')
            f.write('-- 总计: ' + str(len(self.found_words)) + ' 个单词\n')
            f.write('-- 注意：已更新为UK/US音标分开存储\n')
            f.write('-- 临时禁用外键检查，以允许TRUNCATE被引用的表\n')
            f.write('SET FOREIGN_KEY_CHECKS = 0;\n')
            f.write('TRUNCATE TABLE words;\n')
            f.write('SET FOREIGN_KEY_CHECKS = 1;\n\n')

            for word_data in self.found_words:
                word = word_data['word']
                phonetic_uk = f"'{word_data['phonetic_uk'].replace("'", "''")}'" if word_data['phonetic_uk'] else 'NULL'
                phonetic_us = f"'{word_data['phonetic_us'].replace("'", "''")}'" if word_data['phonetic_us'] else 'NULL'
                meaning = word_data['meaning'].replace("'", "''")
                examples = word_data['examples']

                # 处理第一个例句
                if examples:
                    ex = examples[0]
                    example = ex['en'].replace("'", "''")
                    example_translation = ex['cn'].replace("'", "''")

                    # 写入主表记录（包含例句）
                    audio_uk = f"'{word_data['audio_url_uk']}'" if word_data.get('audio_url_uk') else 'NULL'
                    audio_us = f"'{word_data['audio_url_us']}'" if word_data.get('audio_url_us') else 'NULL'

                    f.write(f"INSERT INTO words (list_id, word, phonetic_uk, phonetic_us, audio_url_uk, audio_url_us, meaning, example, example_translation) "
                           f"VALUES (1, '{word}', {phonetic_uk}, {phonetic_us}, {audio_uk}, {audio_us}, "
                           f"'{meaning}', '{example}', '{example_translation}');\n")
                else:
                    # 写入主表记录（没有例句）
                    audio_uk = f"'{word_data['audio_url_uk']}'" if word_data.get('audio_url_uk') else 'NULL'
                    audio_us = f"'{word_data['audio_url_us']}'" if word_data.get('audio_url_us') else 'NULL'

                    f.write(f"INSERT INTO words (list_id, word, phonetic_uk, phonetic_us, audio_url_uk, audio_url_us, meaning) "
                           f"VALUES (1, '{word}', {phonetic_uk}, {phonetic_us}, {audio_uk}, {audio_us}, "
                           f"'{meaning}');\n")

                f.write('\n')

        print(f"\nSQL文件已生成: {output_file}")
        print(f"总计插入: {len(self.found_words)} 个单词")

    def run(self, start_page: int = 1):
        """运行爬虫"""
        print("=" * 60)
        print("Dictionary.net 单词爬虫")
        print("=" * 60)
        print(f"起始页: {start_page}")
        print(f"最大页数: {self.max_pages}")
        print(f"跳过的误拼单词: {self.skipped_spelling_errors}")
        print("=" * 60)

        all_word_urls = []
        current_page = start_page

        # 第一步：爬取索引页获取所有单词链接
        for page in range(start_page, start_page + self.max_pages):
            word_urls = self.crawl_dictionary_page(page)
            if not word_urls:
                print(f"\n第 {page} 页没有找到单词，可能已到最后一页")
                break
            all_word_urls.extend(word_urls)

        print(f"\n总计找到 {len(all_word_urls)} 个单词链接")

        # 第二步：批量爬取详情页
        if all_word_urls:
            word_details = self.crawl_word_details(all_word_urls)
            # 将结果添加到 found_words
            if word_details:
                self.found_words.extend(word_details)

        # 打印统计信息
        print("\n" + "=" * 60)
        print("爬取完成统计:")
        print(f"  索引页爬取: {current_page}")
        print(f"  跳过的误拼: {self.skipped_spelling_errors}")
        print(f"  找到的单词数: {len(self.found_words)}")
        print(f"  生成的SQL文件: words_insert.sql")
        print("=" * 60)

        # 生成SQL文件
        self.generate_sql()


def main():
    if len(sys.argv) > 1:
        try:
            max_pages = int(sys.argv[1])
        except ValueError:
            print("用法: python crawl_dictionary.py [页数]")
            print("示例: python crawl_dictionary.py 100")
            return
    else:
        max_pages = 100

    if len(sys.argv) > 2:
        try:
            start_page = int(sys.argv[2])
        except ValueError:
            start_page = 1
    else:
        start_page = 1

    crawler = DictionaryCrawler(max_pages=max_pages)
    crawler.run(start_page=start_page)


if __name__ == '__main__':
    main()
