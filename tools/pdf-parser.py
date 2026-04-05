"""
한국사능력검정시험 기출문제 PDF 파서
PDF에서 문제, 선택지, 이미지를 추출하여 JSON으로 변환합니다.

사용법:
    python pdf-parser.py --pdf <문제PDF경로> --answer <정답PDF경로> --year 2024 --round 65
    python pdf-parser.py --pdf <문제PDF경로> --answer-list 3,1,4,2,5,... --year 2024 --round 65
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import pdfplumber
from PIL import Image


def extract_text_from_pdf(pdf_path: str) -> list[str]:
    """PDF의 각 페이지에서 텍스트를 추출합니다."""
    pages_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)
    return pages_text


def extract_images_from_pdf(pdf_path: str, output_dir: str, exam_id: str) -> dict[int, str]:
    """PDF에서 이미지를 추출하여 저장합니다. {문제번호: 이미지경로} 반환"""
    images = {}
    os.makedirs(output_dir, exist_ok=True)

    with pdfplumber.open(pdf_path) as pdf:
        img_count = 0
        for page_num, page in enumerate(pdf.pages):
            if page.images:
                for img in page.images:
                    img_count += 1
                    # 이미지를 페이지에서 크롭
                    bbox = (img["x0"], img["top"], img["x1"], img["bottom"])
                    cropped = page.within_bbox(bbox).to_image(resolution=200)
                    img_path = os.path.join(output_dir, f"{exam_id}-img{img_count:03d}.png")
                    cropped.save(img_path)
                    images[img_count] = img_path

    return images


def parse_questions(pages_text: list[str]) -> list[dict]:
    """텍스트에서 문제와 선택지를 파싱합니다."""
    full_text = "\n".join(pages_text)

    # 문제 번호 패턴: "1." 또는 "1 ." 또는 "1)" 등
    # 한국사능력검정시험은 보통 "1." ~ "50." 형식
    question_pattern = re.compile(
        r'(\d{1,2})\s*\.\s*(.*?)(?=\d{1,2}\s*\.|$)',
        re.DOTALL
    )

    # 선택지 패턴: ① ② ③ ④ ⑤ 또는 1 2 3 4 5
    choice_markers = ['①', '②', '③', '④', '⑤']
    choice_pattern = re.compile(
        r'([①②③④⑤])\s*(.*?)(?=[①②③④⑤]|$)',
        re.DOTALL
    )

    questions = []
    matches = question_pattern.findall(full_text)

    for q_num_str, q_body in matches:
        q_num = int(q_num_str)
        if q_num < 1 or q_num > 50:
            continue

        # 선택지 추출
        choice_matches = choice_pattern.findall(q_body)
        choices = []
        question_text = q_body

        if choice_matches:
            # 첫 번째 선택지 앞까지가 문제 텍스트
            first_choice_pos = q_body.find(choice_matches[0][0])
            if first_choice_pos > 0:
                question_text = q_body[:first_choice_pos].strip()

            for i, (marker, text) in enumerate(choice_matches, 1):
                choices.append({
                    "number": i,
                    "text": text.strip()
                })

        # 선택지가 5개가 아닌 경우 대체 파싱 시도
        if len(choices) != 5:
            alt_pattern = re.compile(r'(\d)\s+(.*?)(?=\d\s+|$)', re.DOTALL)
            alt_matches = alt_pattern.findall(q_body)
            if len(alt_matches) >= 5:
                choices = []
                for num_str, text in alt_matches[:5]:
                    choices.append({
                        "number": int(num_str),
                        "text": text.strip()
                    })

        questions.append({
            "id": q_num,
            "question": question_text.strip(),
            "description": None,
            "image": None,
            "choices": choices if len(choices) == 5 else [],
            "answer": None,
            "category": "",
            "era": ""
        })

    # 문제 번호순 정렬
    questions.sort(key=lambda q: q["id"])
    return questions


def parse_answers_from_pdf(pdf_path: str) -> dict[int, int]:
    """정답 PDF에서 정답을 추출합니다."""
    pages_text = extract_text_from_pdf(pdf_path)
    full_text = "\n".join(pages_text)

    answers = {}
    # 정답표 패턴: "1 ③" 또는 "1번 3" 등
    marker_to_num = {'①': 1, '②': 2, '③': 3, '④': 4, '⑤': 5}

    # 패턴 1: 문제번호 + 동그라미 숫자
    pattern1 = re.compile(r'(\d{1,2})\s*([①②③④⑤])')
    for match in pattern1.finditer(full_text):
        q_num = int(match.group(1))
        answer = marker_to_num.get(match.group(2))
        if answer and 1 <= q_num <= 50:
            answers[q_num] = answer

    # 패턴 2: 문제번호 + 일반 숫자
    if len(answers) < 10:
        pattern2 = re.compile(r'(\d{1,2})\s+(\d)\s')
        for match in pattern2.finditer(full_text):
            q_num = int(match.group(1))
            answer = int(match.group(2))
            if 1 <= q_num <= 50 and 1 <= answer <= 5:
                answers[q_num] = answer

    return answers


def parse_answers_from_list(answer_str: str) -> dict[int, int]:
    """쉼표로 구분된 정답 문자열을 파싱합니다. 예: '3,1,4,2,5,...'"""
    answers = {}
    parts = answer_str.split(",")
    for i, part in enumerate(parts, 1):
        part = part.strip()
        if part.isdigit():
            answers[i] = int(part)
    return answers


def build_exam_json(
    year: int,
    round_num: int,
    date: str,
    questions: list[dict],
    answers: dict[int, int]
) -> dict:
    """최종 시험 JSON 데이터를 구성합니다."""
    # 정답 매핑
    for q in questions:
        q["answer"] = answers.get(q["id"])

    return {
        "examId": f"{year}-{round_num}",
        "year": year,
        "round": round_num,
        "date": date,
        "totalQuestions": len(questions),
        "questions": questions
    }


def main():
    parser = argparse.ArgumentParser(description="한국사능력검정시험 PDF 파서")
    parser.add_argument("--pdf", required=True, help="문제 PDF 파일 경로")
    parser.add_argument("--answer", help="정답 PDF 파일 경로")
    parser.add_argument("--answer-list", help="쉼표로 구분된 정답 목록 (예: 3,1,4,2,5,...)")
    parser.add_argument("--year", type=int, required=True, help="시험 연도")
    parser.add_argument("--round", type=int, required=True, help="시험 회차")
    parser.add_argument("--date", default="", help="시험 날짜 (YYYY-MM-DD)")
    parser.add_argument("--output", help="출력 JSON 파일 경로 (기본: data/questions/YYYY-RR.json)")
    parser.add_argument("--extract-images", action="store_true", help="이미지 추출 여부")

    args = parser.parse_args()

    # PDF에서 텍스트 추출
    print(f"PDF 파싱 중: {args.pdf}")
    pages_text = extract_text_from_pdf(args.pdf)
    print(f"  {len(pages_text)}개 페이지 추출 완료")

    # 문제 파싱
    questions = parse_questions(pages_text)
    print(f"  {len(questions)}개 문제 파싱 완료")

    # 정답 파싱
    answers = {}
    if args.answer:
        print(f"정답 PDF 파싱 중: {args.answer}")
        answers = parse_answers_from_pdf(args.answer)
        print(f"  {len(answers)}개 정답 추출 완료")
    elif args.answer_list:
        answers = parse_answers_from_list(args.answer_list)
        print(f"  {len(answers)}개 정답 입력 완료")
    else:
        print("  경고: 정답이 제공되지 않았습니다. answer 필드가 null로 설정됩니다.")

    # 이미지 추출
    if args.extract_images:
        script_dir = Path(__file__).parent.parent
        image_dir = script_dir / "data" / "images"
        exam_id = f"{args.year}-{args.round}"
        print(f"이미지 추출 중...")
        images = extract_images_from_pdf(args.pdf, str(image_dir), exam_id)
        print(f"  {len(images)}개 이미지 추출 완료")

    # JSON 생성
    exam_data = build_exam_json(args.year, args.round, args.date, questions, answers)

    # 파일 저장
    if args.output:
        output_path = args.output
    else:
        script_dir = Path(__file__).parent.parent
        output_path = script_dir / "data" / "questions" / f"{args.year}-{args.round}.json"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(exam_data, f, ensure_ascii=False, indent=2)

    print(f"\n저장 완료: {output_path}")
    print(f"  총 {len(questions)}개 문제, {len(answers)}개 정답 매핑됨")

    # 정답 미매핑 문제 경고
    unmapped = [q["id"] for q in questions if q["answer"] is None]
    if unmapped:
        print(f"  경고: 정답 미매핑 문제: {unmapped}")


if __name__ == "__main__":
    main()
