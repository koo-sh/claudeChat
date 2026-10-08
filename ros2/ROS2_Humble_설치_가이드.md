# Ubuntu 22.04 듀얼부팅 + ROS2 Humble 설치 가이드

> 가천대 TAKE OUT 동아리 자료(「ROS2를 위한 Ubuntu 듀얼부팅 세팅」, 「Take Out ROS2 설치 자료」)를 한 흐름으로 정리하고, 원본 자료에서 그대로 따라 하면 막힐 수 있는 부분을 보완했습니다.

**전체 흐름**

```
백업 → Ubuntu 22.04 설치 USB 만들기 → Windows 디스크 축소 → USB 부팅
     → Ubuntu 설치 → ROS2 Humble 설치 → talker/listener 테스트 → 워크스페이스 생성
```

> ⚠️ **꼭 Ubuntu 22.04 LTS**를 설치하세요. ROS2 Humble은 22.04 전용입니다. 24.04에서는 `ros-humble-*` 패키지가 설치되지 않습니다.

---

## 0단계. 설치 전 준비물

| 항목 | 내용 |
|---|---|
| 백업 | 중요한 파일은 외장하드/클라우드에 먼저 복사 |
| USB | 8GB 이상 (안의 내용은 **전부 삭제됨**) |
| 충전기 | 설치 중 전원이 꺼지면 위험하므로 반드시 연결 |
| 인터넷 | 와이파이 또는 유선랜 (안 되면 휴대폰 USB 테더링) |
| 여유 공간 | Ubuntu용 **80~100GB** 권장 |

### Windows에서 미리 해둘 것 (원본 자료에 없는 내용)

1. **BitLocker / 장치 암호화 확인**
   - 설정 → 개인 정보 및 보안 → 장치 암호화 (또는 제어판 → BitLocker)
   - 켜져 있으면 **복구 키를 먼저 백업**하거나 끄고 진행하세요. BIOS 설정을 바꾸면 Windows 부팅 시 복구 키를 요구할 수 있고, Ubuntu 설치 프로그램이 암호화된 디스크 때문에 멈추기도 합니다.
   - 복구 키 확인: https://account.microsoft.com/devices/recoverykey
2. **빠른 시작 끄기**
   - 제어판 → 전원 옵션 → 전원 단추 작동 설정 → "현재 사용할 수 없는 설정 변경" → **빠른 시작 켜기 체크 해제**
   - 켜져 있으면 Ubuntu에서 Windows 디스크가 잠겨 보이거나 부팅이 꼬일 수 있습니다.

---

## 1단계. Ubuntu 22.04 설치 USB 만들기

1. Ubuntu 22.04 LTS ISO 다운로드: https://releases.ubuntu.com/22.04/
   → `ubuntu-22.04.x-desktop-amd64.iso` (x는 최신 포인트 릴리스)
2. [Rufus](https://rufus.ie) 실행 후 아래처럼 설정

| 항목 | 값 |
|---|---|
| 장치 | 사용할 USB |
| 부트 선택 | 다운받은 Ubuntu ISO |
| 파티션 구성 | **GPT** |
| 대상 시스템 | **UEFI (CSM 없음)** |
| 파일 시스템 | FAT32 |

3. **시작** → (ISO 이미지 모드 권장 선택) → USB 내용 삭제 동의 → 완료될 때까지 대기

---

## 2단계. Windows에서 Ubuntu 공간 만들기

1. Windows 검색창에 **"하드 디스크 파티션 만들기 및 포맷"** 입력 → 실행
2. **C: 드라이브 우클릭 → 볼륨 축소**
3. 축소할 공간에 `81920`~`102400` (MB 단위, 80~100GB) 입력 → 축소
4. 검은색 **"할당되지 않음"** 공간이 생겼는지 확인

> ❌ **절대 Windows 파티션(C:, EFI, 복구 파티션)을 삭제하지 마세요.** 할당되지 않은 공간은 포맷하지 말고 그대로 두면 됩니다.

---

## 3단계. BIOS / Boot Menu에서 USB로 부팅

USB를 꽂은 채로 재부팅하고, 전원이 켜지자마자 아래 키를 여러 번 연타합니다.

| 제조사 | 키 |
|---|---|
| Samsung | F2 또는 F10 |
| LG | F2 또는 F10 |
| Lenovo | F2 / F12 또는 Novo 버튼 |
| ASUS | F2 또는 ESC |
| MSI | DEL 또는 F11 |

> 💡 Windows에서 **Shift 누른 채 "다시 시작"** → 문제 해결 → 고급 옵션 → UEFI 펌웨어 설정 으로도 들어갈 수 있습니다.

확인할 것:
- Boot Mode가 **UEFI**인지
- Boot Menu에서 **USB 이름**(UEFI: ~) 선택
- Ubuntu는 Secure Boot를 지원하므로 **보통은 그대로 두어도 됩니다.** USB 부팅이 안 될 때만 Secure Boot를 OFF 하세요.

GRUB 메뉴가 나오면 **"Try or Install Ubuntu"** 선택.

---

## 4단계. Ubuntu 설치

1. 언어 선택 → **Install Ubuntu**
2. 키보드: Korean 또는 English (US) 편한 것
3. **Normal installation** 선택
   - Download updates while installing: 체크 가능
   - Install third-party software (그래픽/와이파이 드라이버): **체크 권장**
4. ⭐ **가장 중요한 화면 – 설치 형식**
   - "Install Ubuntu alongside Windows Boot Manager"가 보이면 그걸 선택해도 되지만,
   - 안전하게 하려면 **Something else(기타)** 선택 → 2단계에서 만든 **free space(남은 공간)** 클릭 → `+` 버튼 → Mount point `/` 로 지정 → OK
   - "Device for boot loader installation"은 **디스크 전체**(예: `/dev/nvme0n1`)로 두면 됩니다.
   - ❌ **"Erase disk and install Ubuntu"는 절대 선택하지 마세요.** Windows가 통째로 지워집니다.
5. 지역: Seoul → 사용자 이름/비밀번호 설정 → 설치 완료 후 **Restart Now** → 안내가 나오면 USB 제거 후 Enter

---

## 5단계. 설치 후 첫 부팅 체크

재부팅하면 **GRUB 화면**에서 Ubuntu / Windows Boot Manager를 선택할 수 있어야 합니다.

`Ctrl + Alt + T`로 터미널을 열고:

```bash
sudo apt update && sudo apt upgrade -y
lsb_release -a     # Description: Ubuntu 22.04.x LTS 인지 확인
uname -a
locale
```

> 💡 `sudo` 뒤 비밀번호를 입력할 때 **화면에 아무것도 안 뜨는 게 정상**입니다. 그냥 입력하고 Enter.

Wi-Fi, 한글 입력, 화면 해상도도 확인해 둡니다.

---

## 6단계. ROS2 Humble 설치

### 6-1. 로케일(UTF-8) 설정

```bash
locale   # UTF-8 이 보이는지 확인

sudo apt update && sudo apt install -y locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

locale   # 다시 확인
```

### 6-2. Universe 저장소 활성화

```bash
sudo apt install -y software-properties-common
sudo add-apt-repository universe
```

### 6-3. ROS2 저장소 추가

> ⚠️ **원본 자료와 다른 부분.** 원본 자료의 `curl ... ros.key -o /usr/share/keyrings/...` + `echo "deb ..."` 방식은 예전 방법입니다. 2025년 ROS 서명 키가 교체되면서, 현재 공식 문서는 키와 저장소 설정을 자동으로 관리해주는 **`ros2-apt-source` 패키지** 설치 방식으로 바뀌었습니다. 아래 방법을 쓰세요.

```bash
sudo apt update && sudo apt install -y curl

export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')

curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"

sudo dpkg -i /tmp/ros2-apt-source.deb
```

`echo $ROS_APT_SOURCE_VERSION` 결과가 비어 있으면(GitHub API 요청 제한 등) 잠시 후 다시 실행하세요.

### 6-4. 업데이트 후 ROS2 설치

```bash
sudo apt update && sudo apt upgrade -y    # 22.04에서는 ROS 설치 전에 upgrade 필수 (systemd/udev 충돌 방지)
sudo apt install -y ros-humble-desktop    # ROS, RViz, 데모, 튜토리얼 포함 (용량 큼, 시간 좀 걸림)
sudo apt install -y ros-dev-tools         # colcon, rosdep 등 개발 도구
```

### 6-5. 환경 설정 (~/.bashrc)

```bash
gedit ~/.bashrc
```

파일 **맨 아래**에 다음을 붙여넣고 `Ctrl + S` 저장 후 창 닫기:

```bash
source /opt/ros/humble/setup.bash
alias cs='cd ~/ros2_ws/src'
alias cb='cd ~/ros2_ws && colcon build && source install/setup.bash'
```

- `cs` : 워크스페이스 src 폴더로 이동
- `cb` : 워크스페이스 빌드 + 환경 적용

gedit이 싫으면 터미널에서 한 번에 추가해도 됩니다:

```bash
cat >> ~/.bashrc << 'EOF'
source /opt/ros/humble/setup.bash
alias cs='cd ~/ros2_ws/src'
alias cb='cd ~/ros2_ws && colcon build && source install/setup.bash'
EOF
```

(이 명령은 **한 번만** 실행하세요. 여러 번 실행하면 줄이 중복으로 추가됩니다.)

적용:

```bash
source ~/.bashrc
```

---

## 7단계. 설치 확인 – Talker / Listener 예제

지금 터미널을 **닫고**, `Ctrl + Alt + T`로 새 터미널을 3개 엽니다.

```bash
# 터미널 1
ros2 run demo_nodes_cpp talker

# 터미널 2
ros2 run demo_nodes_py listener

# 터미널 3
rqt_graph
```

- 터미널 1에 `Publishing: 'Hello World: 1'` ...
- 터미널 2에 `I heard: [Hello World: 1]` ...
- `rqt_graph` 창에 아래처럼 보이면 **ROS2 설치 완료!**

```
( /talker ) ──/chatter──▶ ( /listener )
```

> rqt_graph에 아무것도 안 보이면 왼쪽 위 🔄(새로고침) 버튼을 눌러보세요.
> 종료는 각 터미널에서 `Ctrl + C`.

---

## 8단계. 워크스페이스 만들기

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
cd ..
cb
ls
```

`ls` 결과에 **`build  install  log  src`** 가 보이면 성공입니다.

> ⚠️ **원본 자료 오류 정정**
> - 원본 슬라이드의 `mkdir –p` 는 하이픈(`-`)이 아니라 **대시(`–`)** 로 되어 있어서, 복사해서 붙여넣으면 `–p`라는 폴더가 생기는 등 오류가 납니다. 반드시 `-p`로 직접 입력하세요.
> - 원본의 "Build devel src가 나타나면 성공"은 ROS1(catkin) 기준입니다. ROS2(colcon)에서는 **`build install log src`** 가 정상입니다.
> - src가 비어 있으면 `Summary: 0 packages finished` 라고 나오는데, 에러가 아니라 정상입니다.

---

## 9단계. (선택) Terminator – 터미널 분할 툴

```bash
sudo apt install -y terminator
```

| 동작 | 단축키 |
|---|---|
| 새 터미널 | `Ctrl + Alt + T` |
| 수평 분할 | `Ctrl + Shift + O` |
| 수직 분할 | `Ctrl + Shift + E` |
| 다음 창으로 | `Ctrl + Tab` |
| 이전 창으로 | `Ctrl + Shift + Tab` |
| 현재 창 닫기 | `Ctrl + Shift + W` |
| 전체 종료 | `Ctrl + Shift + Q` |
| 전체 화면 | `F11` |

talker / listener / rqt_graph를 한 창에서 띄울 때 편합니다.

---

## 자주 막히는 지점 (트러블슈팅)

| 증상 | 해결 |
|---|---|
| Boot Menu에 USB가 안 보임 | 다른 USB 포트 사용, BIOS가 UEFI 모드인지, Rufus를 GPT/UEFI로 만들었는지 확인. 그래도 안 되면 Secure Boot OFF |
| 설치 프로그램이 "BitLocker를 끄라"고 함 | Windows로 돌아가 BitLocker/장치 암호화 해제 후 다시 시도 |
| 설치 후 Windows만 켜짐 | BIOS Boot Order에서 **ubuntu**를 1순위로, 또는 Boot Menu에서 ubuntu 선택 |
| GRUB에 Windows가 안 보임 | Ubuntu에서 `sudo update-grub` |
| 와이파이 안 잡힘 | 유선랜/휴대폰 USB 테더링 연결 → "소프트웨어 & 업데이트 → 추가 드라이버"에서 드라이버 설치 |
| Windows 시간과 Ubuntu 시간이 다름 | Ubuntu에서 `timedatectl set-local-rtc 1 --adjust-system-clock` |
| `ros2: command not found` | `source /opt/ros/humble/setup.bash`가 `~/.bashrc`에 있는지 확인 후 새 터미널 열기 |
| `Unable to locate package ros-humble-desktop` | Ubuntu 버전이 22.04인지(`lsb_release -a`), 6-2·6-3단계를 했는지, `sudo apt update`를 했는지 확인 |
| `apt update` 때 GPG / `NO_PUBKEY` 에러 | 예전 방식 키가 남아 있는 경우. `sudo rm /etc/apt/sources.list.d/ros2.list` 후 6-3단계(ros2-apt-source) 다시 진행 |
| `cb: command not found` | `~/.bashrc`에 alias 추가 후 `source ~/.bashrc` 했는지 확인 |
| 한글 입력이 안 됨 | 설정 → 키보드 → 입력 소스 추가 → **한국어(Hangul)** 추가, 필요시 `sudo apt install ibus-hangul` 후 재로그인 |

> 막히면 **화면 사진을 찍어서 질문**하세요. 임의로 삭제/포맷 버튼을 누르지 마세요.

---

### 참고

- ROS2 Humble 공식 설치 문서: https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html
- ROS2 Humble 지원 기간: 2027년 5월까지 (LTS)
