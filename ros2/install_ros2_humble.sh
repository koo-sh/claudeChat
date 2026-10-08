#!/usr/bin/env bash
# Ubuntu 22.04 (jammy)에 ROS2 Humble 설치 + 환경 설정 + 워크스페이스 생성
# 사용법:  bash install_ros2_humble.sh
# 여러 번 실행해도 안전합니다 (이미 된 단계는 건너뜀).
set -euo pipefail

step() { echo; echo "==== $* ===="; }
die()  { echo "[오류] $*" >&2; exit 1; }

# ---------------------------------------------------------------- 사전 확인
[ "$(id -u)" -ne 0 ] || die "sudo 없이 일반 사용자로 실행하세요: bash install_ros2_humble.sh"

. /etc/os-release
CODENAME="${UBUNTU_CODENAME:-${VERSION_CODENAME:-}}"
[ "$CODENAME" = "jammy" ] || die "Ubuntu 22.04(jammy)가 아닙니다 (현재: ${PRETTY_NAME}). ROS2 Humble은 22.04 전용입니다."

echo "Ubuntu: ${PRETTY_NAME}  /  아키텍처: $(dpkg --print-architecture)"
echo "중간에 sudo 비밀번호를 물어보면 입력하세요 (입력해도 화면에 안 보이는 게 정상)."
sudo -v

# ---------------------------------------------------------------- 1. 로케일
step "1/7 로케일(UTF-8) 설정"
sudo apt-get update
sudo apt-get install -y locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# ---------------------------------------------------------------- 2. universe
step "2/7 universe 저장소 활성화"
sudo apt-get install -y software-properties-common curl
sudo add-apt-repository -y universe

# ---------------------------------------------------------------- 3. ROS 저장소
step "3/7 ROS2 apt 저장소 추가 (ros2-apt-source)"
# 예전 방식(ros.key + ros2.list)이 남아 있으면 충돌하므로 제거
if [ -f /etc/apt/sources.list.d/ros2.list ]; then
  echo "예전 방식 ros2.list 발견 → 제거"
  sudo rm -f /etc/apt/sources.list.d/ros2.list
fi
if dpkg -s ros2-apt-source >/dev/null 2>&1; then
  echo "ros2-apt-source 이미 설치됨 → 건너뜀"
else
  VER=$(curl -fsSL https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest \
        | grep -F '"tag_name"' | awk -F'"' '{print $4}')
  [ -n "$VER" ] || die "ros-apt-source 버전 확인 실패 (인터넷 연결 또는 GitHub API 제한). 잠시 후 다시 실행하세요."
  curl -fL -o /tmp/ros2-apt-source.deb \
    "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${VER}/ros2-apt-source_${VER}.${CODENAME}_all.deb"
  sudo dpkg -i /tmp/ros2-apt-source.deb
fi

# ---------------------------------------------------------------- 4. 설치
step "4/7 시스템 업그레이드 + ROS2 Humble 설치 (시간 좀 걸립니다)"
sudo apt-get update
sudo apt-get upgrade -y          # 22.04는 ROS 설치 전 upgrade 필수
sudo apt-get install -y ros-humble-desktop ros-dev-tools terminator

# ---------------------------------------------------------------- 5. bashrc
step "5/7 ~/.bashrc 설정"
add_line() { grep -qxF "$1" ~/.bashrc || { echo "$1" >> ~/.bashrc; echo "추가: $1"; }; }
add_line "source /opt/ros/humble/setup.bash"
add_line "alias cs='cd ~/ros2_ws/src'"
add_line "alias cb='cd ~/ros2_ws && colcon build && source install/setup.bash'"

# ---------------------------------------------------------------- 6. rosdep
step "6/7 rosdep 초기화"
if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then
  sudo rosdep init
fi
rosdep update || echo "[경고] rosdep update 실패 — 나중에 'rosdep update' 다시 실행하세요."

# ---------------------------------------------------------------- 7. 워크스페이스
step "7/7 워크스페이스(~/ros2_ws) 생성 및 빌드"
mkdir -p ~/ros2_ws/src
set +u; source /opt/ros/humble/setup.bash; set -u
( cd ~/ros2_ws && colcon build )

# ---------------------------------------------------------------- 확인
step "설치 확인"
set +u; source /opt/ros/humble/setup.bash; set -u
echo "ROS_DISTRO=${ROS_DISTRO:-?}"
command -v ros2 >/dev/null && echo "ros2 명령: OK" || echo "ros2 명령: 없음 (새 터미널에서 다시 확인)"
ls ~/ros2_ws

cat <<'EOF'

========================================================
 설치 완료! 이제 이 터미널을 닫고 새 터미널을 여세요.

 테스트 (터미널 3개, 또는 terminator에서 Ctrl+Shift+O/E로 분할):
   1) ros2 run demo_nodes_cpp talker
   2) ros2 run demo_nodes_py listener
   3) rqt_graph      →  /talker --/chatter--> /listener 보이면 성공
========================================================
EOF
