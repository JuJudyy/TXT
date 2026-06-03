import os
import re
from ebooklib import epub

def create_epub_from_txt(txt_path, epub_path, book_title="My Book", author="Unknown"):
    # 1. 建立 EPUB 書籍物件
    book = epub.EpubBook()
    book.set_identifier('id_1234567890')
    book.set_title(book_title)
    book.set_language('zh-TW')
    book.add_author(author)

    # 2. 讀取 TXT 檔案內容
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 正則表達式：用來自動辨識章節（支援：第一章、第1章、Chapter 1、楔子 等）
    chapter_regex = re.compile(r'^\s*(第[一二三四五六七八九十零百千0-9]+[章回卷節]).*|^\s*(Chapter\s*[0-9]+).*|^\s*(楔子|前言|後記)\s*$', re.IGNORECASE)

    chapters = []
    current_chapter_title = "序幕"
    current_chapter_content = []

    def save_chapter(title, content_list, index):
        """輔助函式：將收集到的段落打包成 EPUB 的章節檔案"""
        if not content_list:
            return None
        
        # 將純文字轉為 HTML 格式
        html_content = f"<h1>{title}</h1>"
        for line in content_list:
            clean_line = line.strip()
            if clean_line:
                html_content += f"<p>{clean_line}</p>"
                
        # 建立 EPUB 章節
        chapter = epub.EpubHtml(title=title, file_name=f'chap_{index:04d}.xhtml', lang='zh-TW')
        chapter.content = html_content
        return chapter

    # 3. 解析文字，依據章節切分內容
    chapter_index = 1
    for line in lines:
        if chapter_regex.match(line):
            # 抓到新章節了！先把舊章節存起來
            if current_chapter_content:
                chap = save_chapter(current_chapter_title, current_chapter_content, chapter_index)
                if chap:
                    book.add_item(chap)
                    chapters.append(chap)
                    chapter_index += 1
            # 更新為新章節的標題與內容
            current_chapter_title = line.strip()
            current_chapter_content = []
        else:
            current_chapter_content.append(line)

    # 儲存最後一章
    if current_chapter_content:
        chap = save_chapter(current_chapter_title, current_chapter_content, chapter_index)
        if chap:
            book.add_item(chap)
            chapters.append(chap)

    # 4. 設定書籍的目錄（TOC）與閱讀順序（Spine）
    book.toc = tuple(chapters)
    
    # 加入導航檔案（EPUB 必要件）
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # 設定閱讀順序
    book.spine = ['nav'] + chapters

    # 5. 寫出成 EPUB 檔案
    epub.write_epub(epub_path, book, {})
    print(f"🎉 轉換成功！EPUB 已儲存至: {epub_path}")

# --- 測試執行 ---
if __name__ == "__main__":
    # 請把這裡換成你電腦裡的 TXT 路徑
    input_txt = "novel.txt" 
    output_epub = "novel.epub"
    
    # 建立一個測試用的 TXT 檔（如果檔案不存在的話）
    if not os.path.exists(input_txt):
        with open(input_txt, 'w', encoding='utf-8') as test_f:
            test_f.write("前言\n這是這本書的介紹。\n\n第一章 冒險的開始\n主角出發了，天氣很好。\n\n第二章 神祕的洞窟\n裡面好黑，什麼都看不見。")

    # 執行轉換
    create_epub_from_txt(input_txt, output_epub, book_title="我的測試小說", author="路人甲")
