import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

st.set_page_config(page_title="MBTI 궁합 보기", page_icon="💞", layout="wide")

# -----------------------------
# 기본 데이터
# -----------------------------
MBTI_TYPES: List[str] = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP"
]

# 간단 설명 (임의 예시)
MBTI_DESC: Dict[str, str] = {
    "INTJ": "전략가 · 장기 계획에 강함",
    "INTP": "사색가 · 논리와 탐구",
    "ENTJ": "지도자 · 목표 달성형",
    "ENTP": "토론가 · 아이디어 폭발",
    "INFJ": "옹호자 · 통찰과 가치",
    "INFP": "중재자 · 이상과 진정성",
    "ENFJ": "선도자 · 사람 중심 조화",
    "ENFP": "활동가 · 영감과 자유",
    "ISTJ": "현실주의자 · 책임감과 규범",
    "ISFJ": "수호자 · 헌신과 배려",
    "ESTJ": "경영자 · 체계와 실행",
    "ESFJ": "사교가 · 돌봄과 협동",
    "ISTP": "장인 · 실전 해결사",
    "ISFP": "모험가 · 감각과 따뜻함",
    "ESTP": "사업가 · 실행과 모험",
    "ESFP": "연예인 · 에너지와 즐거움",
}

# 이미지 URL (핫링크 대신 플레이스홀더 사용)
MBTI_IMG: Dict[str, str] = {t: f"https://via.placeholder.com/480x320.png?text={t}" for t in MBTI_TYPES}

# -----------------------------
# 유틸리티
# -----------------------------

def compatibility_score(a: str, b: str) -> int:
    """아주 단순한 규칙 기반 점수: 같은 글자당 +25 (최대 100)."""
    a, b = a.upper(), b.upper()
    score = 0
    for ch1, ch2 in zip(a, b):
        if ch1 == ch2:
            score += 25
    return score


def letter_insights(a: str, b: str) -> Tuple[List[str], List[str]]:
    """강점 포인트 / 잠재 갈등 포인트 자동 생성"""
    strengths, risks = [], []
    pairs = list(zip(a, b))

    # E/I
    if pairs[0][0] == pairs[0][1]:
        if pairs[0][0] == 'E':
            strengths.append("둘 다 외향적이라 활동 위주의 데이트에 시너지가 납니다.")
        else:
            strengths.append("둘 다 내향적이라 차분한 시간에서 안정감을 느낍니다.")
    else:
        strengths.append("에너지 사용 패턴이 달라 서로 균형을 잡아줄 수 있습니다.")
        risks.append("사회적 활동 빈도에서 충돌이 생길 수 있어요.")

    # S/N
    if pairs[1][0] == pairs[1][1]:
        if pairs[1][0] == 'N':
            strengths.append("미래지향적 대화와 아이디어 교류가 활발합니다.")
        else:
            strengths.append("현실적 문제 해결에서 합이 잘 맞습니다.")
    else:
        strengths.append("아이디어와 현실감각의 조합으로 실행력이 좋아집니다.")
        risks.append("세부 vs. 큰그림 관점 차이로 의사결정이 늘어질 수 있어요.")

    # T/F
    if pairs[2][0] == pairs[2][1]:
        if pairs[2][0] == 'T':
            strengths.append("논리적 합리성에 합의가 쉽습니다.")
        else:
            strengths.append("감정과 관계를 중시해 정서적 지지가 좋습니다.")
    else:
        strengths.append("이성과 감성이 상호 보완됩니다.")
        risks.append("의사결정 기준(사람 vs. 과제)에서 갈등이 생길 수 있어요.")

    # J/P
    if pairs[3][0] == pairs[3][1]:
        if pairs[3][0] == 'J':
            strengths.append("계획과 일정 관리가 수월합니다.")
        else:
            strengths.append("유연하고 자율적인 분위기를 선호합니다.")
    else:
        strengths.append("계획성과 유연성이 균형을 이룹니다.")
        risks.append("정해진 계획 vs. 즉흥성에서 마찰 가능성이 있어요.")

    return strengths, risks


@st.cache_data
def default_matrix() -> pd.DataFrame:
    """기본 16x16 궁합표(동일 문자 +25 규칙)를 생성."""
    mat = np.zeros((16, 16), dtype=int)
    for i, a in enumerate(MBTI_TYPES):
        for j, b in enumerate(MBTI_TYPES):
            mat[i, j] = compatibility_score(a, b)
    df = pd.DataFrame(mat, index=MBTI_TYPES, columns=MBTI_TYPES)
    return df


# -----------------------------
# 사이드바: 옵션 + 사용자 정의 매트릭스 업로드
# -----------------------------
with st.sidebar:
    st.header("⚙️ 옵션")
    use_custom = st.toggle("사용자 정의 궁합표(CSV) 사용", value=False)
    custom_df = None
    if use_custom:
        st.caption("CSV는 16x16 표 형식, 행/열 레이블은 MBTI 코드여야 합니다.")
        file = st.file_uploader("궁합표 CSV 업로드", type=["csv"]) 
        if file is not None:
            try:
                temp = pd.read_csv(file, index_col=0)
                # 형식 검증
                if set(temp.index) >= set(MBTI_TYPES) and set(temp.columns) >= set(MBTI_TYPES):
                    custom_df = temp.reindex(index=MBTI_TYPES, columns=MBTI_TYPES)
                    st.success("사용자 정의 궁합표가 적용되었습니다.")
                else:
                    st.error("행/열 라벨이 MBTI 16종을 모두 포함해야 합니다.")
            except Exception as e:
                st.error(f"CSV 파싱 오류: {e}")

    st.divider()
    st.caption("팁: 좌측 상단의 돋보기 검색으로 MBTI 카드와 페어를 빠르게 찾을 수 있어요.")

# 실제로 사용할 매트릭스
MATRIX = custom_df if use_custom and custom_df is not None else default_matrix()

# -----------------------------
# 헤더
# -----------------------------
col1, col2 = st.columns([1, 2], gap="large")
with col1:
    st.title("💞 MBTI 궁합 보기")
    st.write("두 사람의 MBTI를 선택하거나 검색해서 궁합을 확인하세요.")
with col2:
    # 검색바: 유형/설명 전체에서 검색
    query = st.text_input("🔎 MBTI 또는 페어 검색 (예: ENFP, INTJ, ENFP-INTJ)")

# -----------------------------
# 검색 결과 섹션
# -----------------------------
if query:
    q = query.strip().upper().replace(" ", "")
    st.subheader("검색 결과")

    # 페어 검색(ENFP-INTJ 형태)
    pair_hit = None
    if "-" in q and len(q.split("-")) == 2:
        a, b = q.split("-")
        if a in MBTI_TYPES and b in MBTI_TYPES:
            pair_hit = (a, b)

    if pair_hit:
        a, b = pair_hit
        st.markdown(f"**페어 매치:** `{a} - {b}`")
        score = int(MATRIX.loc[a, b]) if (a in MATRIX.index and b in MATRIX.columns) else compatibility_score(a, b)
        st.progress(score/100.0, text=f"궁합 점수: {score}/100")
        s_list, r_list = letter_insights(a, b)
        c1, c2 = st.columns(2)
        with c1:
            st.image([MBTI_IMG[a], MBTI_IMG[b]], caption=[a, b], use_column_width=True)
        with c2:
            st.write("### 강점")
            for s in s_list:
                st.write("- ", s)
            st.write("### 주의/갈등 포인트")
            for r in r_list:
                st.write("- ", r)
    else:
        # 타입 검색
        hits = [t for t in MBTI_TYPES if q in t or q in MBTI_DESC.get(t, "").upper()]
        if hits:
            cols = st.columns(4)
            for i, t in enumerate(hits):
                with cols[i % 4]:
                    st.image(MBTI_IMG[t], caption=t, use_column_width=True)
                    st.caption(MBTI_DESC.get(t, ""))
        else:
            st.info("검색 결과가 없습니다. 예: `ENFP-INTJ` 또는 `INTJ`")

st.divider()

# -----------------------------
# 메인 인터랙션: 타입 선택 → 궁합 계산
# -----------------------------
left, right = st.columns(2)
with left:
    my_mbti = st.selectbox("당신의 MBTI", MBTI_TYPES, index=7)  # ENFP 기본
with right:
    other_mbti = st.selectbox("상대방의 MBTI", MBTI_TYPES, index=0)  # INTJ 기본

score = int(MATRIX.loc[my_mbti, other_mbti]) if (my_mbti in MATRIX.index and other_mbti in MATRIX.columns) else compatibility_score(my_mbti, other_mbti)

# 상단 요약 카드
k1, k2, k3 = st.columns(3)
with k1:
    st.metric("궁합 점수", f"{score}/100")
with k2:
    match_level = "아주 높음" if score >= 75 else ("보통" if score >= 50 else ("낮음" if score >= 25 else "도전적"))
    st.metric("궁합 등급", match_level)
with k3:
    same_letters = sum(1 for a,b in zip(my_mbti, other_mbti) if a==b)
    st.metric("일치 성향 수", f"{same_letters}/4")

# 이미지 & 설명
img_col, text_col = st.columns([1, 1])
with img_col:
    st.image([MBTI_IMG[my_mbti], MBTI_IMG[other_mbti]], caption=[my_mbti, other_mbti], use_column_width=True)
with text_col:
    st.subheader("관계 인사이트")
    strengths, risks = letter_insights(my_mbti, other_mbti)
    st.markdown("**강점**")
    for s in strengths:
        st.write("- ", s)
    st.markdown("**주의/갈등 포인트**")
    for r in risks:
        st.write("- ", r)

# 추천 활동(아주 단순 규칙)
st.subheader("추천 활동 & 팁")
recs: List[str] = []
if my_mbti[0] == 'E' or other_mbti[0] == 'E':
    recs.append("바깥 활동(전시, 플리마켓, 가벼운 운동)으로 에너지 발산")
else:
    recs.append("카페 탐방, 보드게임, 홈쿠킹 같은 조용한 일정")
if my_mbti[1] != other_mbti[1]:
    recs.append("아이디어(큰 그림)와 계획(세부)를 분담해 하나의 프로젝트로 묶기")
if my_mbti[2] != other_mbti[2]:
    recs.append("의사결정 시 '사람 영향'과 '논리 근거' 체크리스트를 함께 사용")
if my_mbti[3] != other_mbti[3]:
    recs.append("데이트 전 기대치(시간/예산/유연성)를 미리 합의")
for r in recs:
    st.write("- ", r)

st.divider()

# -----------------------------
# 전체 궁합표(히트맵 스타일 표)
# -----------------------------
st.subheader("전체 궁합표 (16×16)")
st.caption("사이드바에서 CSV를 업로드해 커스텀 점수를 적용할 수 있어요.")
styled = MATRIX.style.format("{:.0f}").background_gradient(cmap="RdYlGn", axis=None)
st.dataframe(styled, use_container_width=True)

# 푸터
st.caption("※ 본 앱의 평가는 간단한 규칙 기반이며, 재미/참고용입니다.")
