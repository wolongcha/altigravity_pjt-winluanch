# ⚡ Antigravity CLI Windows Launcher (`winluanch`)

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Antigravity CLI(`agy`)를 Windows 환경에서 손쉽게 부팅 시 자동 실행하거나, 과거 수행했던 대화 세션 목록을 조회하여 원클릭으로 이어하기(Resume)할 수 있는 데스크톱 런처 GUI 애플리케이션입니다.

---

## 🌟 주요 기능

- **🚀 1-Click Quick Launch**: 
  - `🚀 새 세션 바로 실행`: 지정한 디렉토리에서 PowerShell 개시 후 `agy` 실행
  - `⏩ 최근 세션 이어하기`: 가장 최근 대화 맥락을 이어받아 `agy -c` 실행
- **🤖 AUTO 모드 지원**:
  - `--dangerously-skip-permissions` 기본 활성화로 도구 실행 시 자동 승인 처리
- **📜 과거 세션 히스토리 탐색**:
  - `C:\Users\aceyo\.gemini\antigravity-cli\brain` 디렉토리 자동 스캔
  - 세션별 첫 요청(제목), 최종 수정 일시, 세션 ID, 질문 횟수 표시
  - `▶️ 이 세션 이어하기`: 해당 특정 세션 ID로 `agy --conversation <SESSION_ID>` 실행
  - `🔍 대화 보기`: 세션 내 질문/프롬프트 이력 미리보기
  - `🔍 실시간 검색`: 세션 제목 및 ID 검색 필터링
- **🪟 Windows 시스템 연동**:
  - Windows 부팅 시 자동 실행 등록/해제 기능 (`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`)
  - 바탕화면 및 시작 메뉴 바로가기 생성

---

## 🛠️ 개발 및 빌드 안내

```bash
# 디렉토리 이동
cd C:\Users\aceyo\antigravity\winluanch

# 소스코드 직접 실행
python app.py

# 독립 실행 파일(.exe) 빌드
python build_exe.py

# 프로그램 설치 및 바로가기 생성
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

---

## 👤 작성자 정보

- **GitHub**: [wolongcha](https://github.com/wolongcha)
- **Repository**: [wolongcha/altigravity_pjt-winluanch](https://github.com/wolongcha/altigravity_pjt-winluanch)
- **E-Mail**: wolongcha@gmail.com
