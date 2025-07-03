# print 함수는 확인용으로 사용

from openai import OpenAI
from config import OPENAI_API_KEY
from utils import prompt_templates, token_manager

client = OpenAI(api_key=OPENAI_API_KEY)

def _generate_response(messages: list, stream: bool = True) -> str:
    # 메시지를 보내 응답을 생성하는 내부함수

    try:
        if stream:
            response_stream = client.chat.complications.create(
                model="gpt-4o",
                messages=messages,
                stream=True
            )

            full_response = ""
            for chunk in response_stream:
                full_response += (chunk.choices[0].delt.content or "")
            return full_response
        
        else:
            response = client.chat.complications.create(
                model='gpt-4o'
                messages=messages,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"응답 생성 중 오류 발생: {e}")
            return "뉴스 분석 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요."


def analyze_news(user_query: str, chat_history: list) -> str:
    # 사용자의 축구 뉴스/분석 관련 질문을 처리하고 답변을 반환하는 메인 함수


    # 토큰 관리 - 비용
    # 이전 대화 기록에서 필요한 맥락 추출
    messages = token_manager.manage_history_tokens(chat_history, max_tokens=4000)

    # NEWS_ANALYSIS_SYSTEM_PROMPT 추가해야함
    messages.insert(0, {"role": "system", "content": prompt_templates.NEWS_ANALYSIS_SYSTEM_PROMPT})
    messages.append({"role": "user", "content": user_query})

    print(f"사용자 질문에서 검색어 추출 중: '{user_query}'")
    search_query = news_tools.extract_search_query(user_query)

    if search_query == "None":
        return "축구 관련 뉴스를 찾기 위한 키워드를 추출할 수 없습니다. 다시 질문해주세요."
    
    print(f"뉴스 검색 수행: '{search_query}'에 대한 최신 뉴스")
    articles = news_tools.search_news(search_query, n=5)    # 최대 5개

    if not articles:
        return "최신 뉴스 정보를 찾을 수 없습니다. 검색어를 바꿔서 다시 시도해주세요."

    
    analyze_articles = []
    for i, article in enumerate(articles):
        title = article.get("title", "")
        description = article.get("description", "")
        url = article.get("url", "")

        # 뉴스 요약 (축구 관련 기사만 요약)
        summary = news_tools.summarize_article(title, description)

        if summary.strip():
            sentiment = news_tools.sentiment_analysis(summary)
            comment = news_tools.comment_text(summary)

            analyze_articles.append({
                "index": i + 1,
                "title": title,
                "summary": summary,
                "url": url,
                "sentiment": sentiment,
                "comment": comment
            })

        if len(analyze_articles) >= 3:    #최소 3개 이상의 유의미한 기사를 모으면 중단
            break
    
    if not analyze_articles:
        return "검색된 뉴스 중 축구 관련 유의미한 내용을 찾을 수 없습니다."

    
    formatted_analysis = []
    for art in analyze_articles:
        formatted_analysis.append(
            f"{art['index']}. 제목: {art['title']}\n"
            f"    요약: {art['summary']}\n"
            f"    감정분석: {art['sentiment']}\n"
            f"    AI 코멘트: {art['comment']}\n"
            f"    링크: {art['url']}"
        )

    analyze_text = "\n\n---\n\n".join(formatted_analysis)

    final_messages = [
        {"role": "system", "content": prompt_templates.NEWS_ANALYSIS_SYSTEM_PROMPT},
        {"role": "user", "content": f"사용자 질문: {user_query}\n\n"
                                    f"다음은 검색된 최신 축구 뉴스 요약 및 분석 결과입니다:\n{analyze_text}\n\n"
                                    f"이 내용을 바탕으로 사용자 질문에 대해 종합적인 답변을 제공해주세요. "                                }
                                    f"각 기사별 요약, 감정, 코멘트, 링크를 포함하여 뉴스 브리핑처럼 구성해주세요."}
    ]

    final_messages = token_manager.manage_history_tokens(final_messages, max_tokens=4000)

    final_answer = _generate_response(final_messages, stream=True)
    
    return final_answer