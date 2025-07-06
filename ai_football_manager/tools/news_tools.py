import requests
import json
from openai import OpenAI
from config import OPENAI_API_KEY, NEWS_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def extract_search_query(user_input: str) -> str:
	# 사용자 입력에서 뉴스 검색을 위한 핵심 키워드(선수명, 팀명, 리그명)를 추출

	response = client.chat.completions.create(
		model="gpt-4o",
		messages=[{
					"role": "system",
					"content": """
						사용자가 축구 선수, 축구팀, 리그의 근황을 물어보면,
						그 질문에서 핵심 키워드(선수명, 팀명, 리그명)만 간단히 반환해줘.
						예를 들어:
						- '손흥민 근황 알려줘'라면 '손흥민'
						- '토트넘 경기 일정 알려줘'라면 '토트넘'
						- '프리미어리그 최신 소식'이라면 '프리미어리그'
						- '맨유'는 '맨체스터 유나이티드'로 
						라고만 반환해.

						만약 축구와 관련 없는 질문이라면 'None'이라고 반환해.
					"""
				},
				{"role": "user", "content": user_input}
		],
		temperature=0.0,    # 분류 -> 정확성 우선
		max_tokens=20	   # 짧은 키워드만 필요
	)
	return response.choices[0].message.content.strip()

def search_news(query: str, n: int = 5) -> list:
	# News API를 사용해 최신 축구 뉴스를 검색하고 기사 목록을 반환

	if not NEWS_API_KEY:
		print("경고: NEWS_API_KEY가 설정 되지 않음. 뉴스 검색 수행 불가")
		return []

	url = f"https://newsapi.org/v2/everything?q={query}&language=ko&sortBy=publishedAt&pageSize={n}&apiKey={NEWS_API_KEY}"

	try:
		response = requests.get(url, timeout=10)
		response.raise_for_status()    # HTTP 오류 발생시 예외 발생
		data = response.json()
		# print(f"[DEBUG] 뉴스 API 응답: {data}")  # 디버깅용 로그
		return data.get("articles", [])
	except requests.exceptions.RequestException as e:
		print(f"뉴스 API 호출 중 오류 발생: {e}")
		return []
	except json.JSONDecodeError as e:
		print(f"뉴스 API 응답 파싱 중 오류 발생: {e}")
		return []


def summarize_article(title: str, description: str) -> str:
	# 뉴스 기사의 제목과 설명을 바탕으로 축구 관련 기사인지 판단하고 요약

	prompt = f"""
	아래는 뉴스 기사 제목과 설명이야.
	만약 축구와 관련된 기사라면, 한국어로 간단하게 요약해줘.
	축구와 관련이 없다면 아무 말도 하지 말고 그냥 빈칸으로 둬.

	제목: {title}
	설명: {description}
	"""

	response = client.chat.completions.create(
		model="gpt-4o",
		messages=[{"role": "system", "content": "너는 유능한 축구 기자야. 간결하게 요약해."},
				  {"role": "user", "content": prompt}
		],
		max_tokens=150
	)
	return response.choices[0].message.content.strip()


def sentiment_analysis(summary: str) -> str:
	# 뉴스 요약이 축구팬에게 긍정, 부정, 중립 중 무엇인지 한 단어로 분석

	prompt = f"아래 뉴스 요약이 축구팬에게 긍정, 부정, 중립 중 무엇인지 한 단어로만 답해줘.\n\n{summary}"

	response = client.chat.completions.create(
		model="gpt-4o",
		messages=[{"role": "user", "content": prompt}],
		max_tokens=10,
		temperature=0.0
	)
	return response.choices[0].message.content.strip()

def comment_text(summary: str) -> str:
	# 해외축구 뉴스 요약에 대해 축구팬 입장에서 한줄 코멘트를 남김
	prompt = "아래는 해외축구 뉴스 요약이야. 축구팬 입장에서 한줄 코멘트를 남겨줘. \n\n{summary}"
	response = client.chat.completions.create(
		model="gpt-4o",
		messages=[{"role": "user", "content": prompt}],
		max_tokens=50
	)
	return response.choices[0].message.content.strip()