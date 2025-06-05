# 🔧 서브모듈 기반 협업 가이드 (ChatRPGProject)

번 프로젝트는 두 개의 동맹된 저장소(`android-client`, `backend-fastapi`)를 **Git Submodule**로 포함하여 관리합니다.

---

## 프로젝트 구조

```
ChatRPGProject/
├── android-client/       # Kotlin 기반 안드로이드 클라이언트 (feature/android)
├── backend-fastapi/      # Python 기반 FastAPI 서버 (feature/llm)
├── README.md
├── .gitignore
├── .gitmodules
└── ...
```

---

## 프로젝트 클로드 (첫 참여 후)

```bash
git clone --recurse-submodules git@github.com:2025-Practical-Coding/Mash-potatoes.git
cd ChatRPGProject
```

이미 클로드했다면:

```bash
git submodule update --init --recursive
```

---

## 서브모듈 업데이트 (최신 커미트 동기화)

```bash
git submodule update --remote --merge
git add android-client backend-fastapi
git commit -m "서브모듈 최신 커미트 반사"
git push origin dev  # 또는 main
```

---

## 각 팀원의 작업 방식

### 하드컵: 안드로이드 단장 (Kotlin)

```bash
cd android-client
git checkout feature/android
# 작업, 커미트, 푸셔
```

dev 또는 main에 포트 반사:

```bash
cd ..
git add android-client
git commit -m "android-client 서브모듈 커미트 업데이트"
git push origin dev
```

### 백업: 바크엣드 단장 (Python)

```bash
cd backend-fastapi
git checkout feature/llm
# 작업, 커미트, 푸셔
```

메인에 업데이트 반사:

```bash
cd ..
git add backend-fastapi
git commit -m "backend-fastapi 서브모듈 커미트 업데이트"
git push origin dev
```

---

## 자동화 스크립트 (선택)

### `update-submodules.sh`

```bash
#!/bin/bash
git submodule update --remote --merge
git add android-client backend-fastapi
git commit -m "서브모듈 최신 커미트 자동 반사"
git push origin dev
```

> Git Bash / WSL / macOS / Linux 환경에서 사용가능

---

## 주의 사항

* 서브모듈 디렉토리에서 직접 `git push` 해야 변경 사항이 반영됩니다.
* 메인 레포에서는 변경된 서브모듈 포인터를 `add` 후 `commit`해야 반영됩니다.
* `.gitmodules`가 변경되면 반드시 커밋해주세요.

---

## 참고

* [https://git-scm.com/book/en/v2/Git-Tools-Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
* [https://docs.github.com/en/get-started/working-with-submodules](https://docs.github.com/en/get-started/working-with-submodules)
