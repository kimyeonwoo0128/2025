import streamlit as st

st.title("MBTI 궁합 테스트")
st.write("두 사람의 MBTI 유형을 선택하면 궁합을 알려드립니다!")

mbti_types = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP"
]

# 사용자 입력
my_mbti = st.selectbox("당신의 MBTI를 선택하세요:", mbti_types)
other_mbti = st.selectbox("상대방의 MBTI를 선택하세요:", mbti_types)

# 점수 계산
score = 0
for a, b in zip(my_mbti, other_mbti):
    if a == b:
        score += 25

# 결과 출력
st.subheader("궁합 결과")
st.write(f"**궁합 점수: {score}점 / 100점**")

# 관계 설명 (간단 버전)
if score >= 75:
    desc = "성향이 매우 비슷해 금방 친해질 수 있어요!"
elif score >= 50:
    desc = "비슷한 부분도 있고 다른 부분도 있어 균형이 좋습니다."
elif score >= 25:
    desc = "성향 차이가 다소 있지만 노력하면 시너지가 납니다."
else:
    desc = "거의 정반대 성향! 하지만 끌릴 수도 있죠 😉"

st.info(desc)

