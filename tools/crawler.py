"""
한국사능력검정시험 기출문제 크롤러
공식 사이트에서 기출문제 PDF와 정답을 다운로드합니다.

사용법:
    python crawler.py --list                    # 다운로드 가능한 회차 목록 확인
    python crawler.py --download 65             # 특정 회차 다운로드
    python crawler.py --download-all            # 전체 다운로드
    python crawler.py --download-range 60 65    # 범위 다운로드
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.historyexam.go.kr"
EXAM_LIST_URL = f"{BASE_URL}/pageLink.do?link=oldExamList&netfunnel_key="
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "raw"


def get_exam_list() -> list[dict]:
    """공식 사이트에서 기출문제 목록을 가져옵니다."""
    print("기출문제 목록을 가져오는 중...")

    try:
        resp = requests.get(EXAM_LIST_URL, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"사이트 접속 실패: {e}")
        print("사이트 구조가 변경되었을 수 있습니다. URL을 확인해주세요.")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    exams = []

    # 사이트 구조에 따라 파싱 로직 조정 필요
    # 일반적으로 테이블이나 리스트 형태로 회차 정보가 표시됨
    rows = soup.select("table tbody tr") or soup.select(".exam-list li")

    for row in rows:
        try:
            # 회차, 날짜, 다운로드 링크 추출 (사이트 구조에 따라 조정)
            text = row.get_text(strip=True)
            links = row.select("a[href]")

            # 회차 번호 추출
            round_match = re.search(r"(\d+)\s*회", text)
            if not round_match:
                continue

            round_num = int(round_match.group(1))

            # 다운로드 링크 추출
            pdf_links = {}
            for link in links:
                href = link.get("href", "")
                link_text = link.get_text(strip=True)
                if "문제" in link_text or "question" in href.lower():
                    pdf_links["question"] = href if href.startswith("http") else BASE_URL + href
                elif "정답" in link_text or "answer" in href.lower():
                    pdf_links["answer"] = href if href.startswith("http") else BASE_URL + href

            exams.append({
                "round": round_num,
                "text": text[:80],
                "links": pdf_links,
            })
        except Exception as e:
            continue

    return sorted(exams, key=lambda x: x["round"], reverse=True)


def download_file(url: str, output_path: str) -> bool:
    """파일을 다운로드합니다."""
    try:
        resp = requests.get(url, headers=HEADERS, stream=True, timeout=30)
        resp.raise_for_status()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        size_kb = os.path.getsize(output_path) / 1024
        print(f"  다운로드 완료: {output_path} ({size_kb:.1f} KB)")
        return True
    except Exception as e:
        print(f"  다운로드 실패: {url} - {e}")
        return False


def download_exam(round_num: int, exams: list[dict]) -> bool:
    """특정 회차의 문제와 정답을 다운로드합니다."""
    exam = next((e for e in exams if e["round"] == round_num), None)
    if not exam:
        print(f"  {round_num}회 정보를 찾을 수 없습니다.")
        return False

    print(f"\n제{round_num}회 다운로드 중...")

    success = True
    links = exam.get("links", {})

    if "question" in links:
        q_path = str(OUTPUT_DIR / f"{round_num}-question.pdf")
        if not download_file(links["question"], q_path):
            success = False
    else:
        print(f"  문제 PDF 링크를 찾을 수 없습니다.")
        success = False

    if "answer" in links:
        a_path = str(OUTPUT_DIR / f"{round_num}-answer.pdf")
        if not download_file(links["answer"], a_path):
            success = False
    else:
        print(f"  정답 PDF 링크를 찾을 수 없습니다.")

    return success


def update_index(downloaded_rounds: list[int]):
    """index.json을 업데이트합니다."""
    index_path = Path(__file__).parent.parent / "data" / "index.json"

    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            index = json.load(f)
    else:
        index = {"exams": [], "categories": [], "eras": []}

    existing_ids = {e["examId"] for e in index["exams"]}

    for round_num in downloaded_rounds:
        exam_id = f"{round_num}"
        if exam_id not in existing_ids:
            index["exams"].append({
                "examId": exam_id,
                "year": 0,
                "round": round_num,
                "date": "",
                "totalQuestions": 50,
                "file": f"questions/{exam_id}.json"
            })

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f"\nindex.json 업데이트 완료")


def main():
    parser = argparse.ArgumentParser(description="한국사능력검정시험 기출문제 크롤러")
    parser.add_argument("--list", action="store_true", help="다운로드 가능한 회차 목록 표시")
    parser.add_argument("--download", type=int, help="특정 회차 다운로드")
    parser.add_argument("--download-all", action="store_true", help="전체 회차 다운로드")
    parser.add_argument("--download-range", nargs=2, type=int, metavar=("FROM", "TO"),
                        help="범위 다운로드 (예: 60 65)")

    args = parser.parse_args()

    if not any([args.list, args.download, args.download_all, args.download_range]):
        parser.print_help()
        return

    exams = get_exam_list()

    if args.list:
        if not exams:
            print("목록을 가져올 수 없습니다. 사이트를 직접 확인해주세요.")
            print(f"URL: {BASE_URL}")
            return
        print(f"\n총 {len(exams)}개 회차:")
        for exam in exams:
            links = exam.get("links", {})
            link_info = ", ".join(links.keys()) if links else "링크 없음"
            print(f"  제{exam['round']}회 - {link_info}")
        return

    if not exams:
        print("시험 목록을 가져올 수 없습니다.")
        return

    downloaded = []

    if args.download:
        if download_exam(args.download, exams):
            downloaded.append(args.download)

    elif args.download_all:
        for exam in exams:
            if download_exam(exam["round"], exams):
                downloaded.append(exam["round"])
            time.sleep(1)  # 서버 부하 방지

    elif args.download_range:
        start, end = args.download_range
        for exam in exams:
            if start <= exam["round"] <= end:
                if download_exam(exam["round"], exams):
                    downloaded.append(exam["round"])
                time.sleep(1)

    if downloaded:
        print(f"\n총 {len(downloaded)}개 회차 다운로드 완료: {downloaded}")
    else:
        print("\n다운로드된 파일이 없습니다.")


if __name__ == "__main__":
    main()
