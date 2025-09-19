import json
from datetime import date, datetime, time
from typing import List, Dict, Any, Union, Optional

from google import genai
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from model.database import get_db
from model.user.crud import user_crud
from model.category.crud import category_crud
from model.schedule.event.crud import event_crud
from model.schedule.task.crud import task_crud
from model.schedule.participant.crud import participant_crud
from model.schedule.alert.crud import alert_crud
from model.user import models as user_models
from model.schedule.event import models as event_models
from model.schedule.task import models as task_models
from model.schedule.participant import models as participant_models
from model.schedule.alert import models as alert_models
from model.schedule.visibility import Visibility
from model.ai.schemas import (
    CreateFromTextRequest, CategoryInfo, AIEventResponse, 
    AITaskResponse, AIResponse
)
from core.config import settings


class CustomException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class AiService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        if settings.GEMINI_API_KEY:
            # The user has provided a GEMINI_API_KEY in the config.
            # The genai.Client() is expected to use the GEMINI_API_KEY environment variable.
            # We assume the environment is configured correctly to expose this key.
            # For example, by using a .env file that is loaded on startup.
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.client = genai.Client()
        else:
            self.client = None

    def create_from_text(self, request: CreateFromTextRequest, username: str) -> Union[AIEventResponse, AITaskResponse]:
        """텍스트로부터 EVENT 또는 TASK 생성 (인증된 사용자용)"""
        user = user_crud.get_user_by_email_or_phone(self.db, username)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        user_categories = category_crud.find_by_user_order_by_created(self.db, user)
        category_infos = [CategoryInfo(id=c.id, name=c.name) for c in user_categories]

        parsed_result = self._parse_text_with_ai(request.text, category_infos)
        
        if not parsed_result:
            raise CustomException(status_code=status.HTTP_400_BAD_REQUEST, detail="텍스트 분석에 실패했습니다")

        schedule_type = parsed_result.get("type", "").upper()

        if schedule_type == "EVENT":
            return self._create_event_from_parsed_result(parsed_result, user, user_categories, request.text)
        elif schedule_type == "TASK":
            return self._create_task_from_parsed_result(parsed_result, user, user_categories, request.text)
        else:
            raise CustomException(status_code=status.HTTP_400_BAD_REQUEST, detail="올바른 스케줄 타입을 인식하지 못했습니다")

    def create_from_text_trial(self, request: CreateFromTextRequest) -> Union[AIEventResponse, AITaskResponse]:
        """텍스트로부터 EVENT 또는 TASK 생성 (체험용)"""
        category_infos = [CategoryInfo(id=1, name="일정")]

        parsed_result = self._parse_text_with_ai(request.text, category_infos)
        
        if not parsed_result:
            raise CustomException(status_code=status.HTTP_400_BAD_REQUEST, detail="텍스트 분석에 실패했습니다")

        schedule_type = parsed_result.get("type", "").upper()

        if schedule_type == "EVENT":
            return AIEventResponse(
                name=parsed_result.get("name", ""),
                location=parsed_result.get("location"),
                start_date=date.fromisoformat(parsed_result["startDate"]),
                end_date=date.fromisoformat(parsed_result["endDate"]),
                start_time=time.fromisoformat(parsed_result["startTime"]) if parsed_result.get("startTime") else None,
                end_time=time.fromisoformat(parsed_result["endTime"]) if parsed_result.get("endTime") else None,
                visibility="PRIVATE",
                color="#0090FF"
            )
        elif schedule_type == "TASK":
            return AITaskResponse(
                name=parsed_result.get("name", ""),
                location=parsed_result.get("location"),
                start_time=datetime.fromisoformat(parsed_result["startTime"]) if parsed_result.get("startTime") else None,
                end_time=datetime.fromisoformat(parsed_result["endTime"]) if parsed_result.get("endTime") else None,
                scheduled_time=datetime.fromisoformat(parsed_result["scheduledTime"]) if parsed_result.get("scheduledTime") else None,
                is_completed=False,
                visibility="PRIVATE",
                color="#0090FF"
            )
        else:
            raise CustomException(status_code=status.HTTP_400_BAD_REQUEST, detail="올바른 스케줄 타입을 인식하지 못했습니다")

    def _create_event_from_parsed_result(
        self, 
        result: Dict[str, Any], 
        user: user_models.User, 
        user_categories: List, 
        source_text: str
    ) -> AIEventResponse:
        """파싱된 결과로부터 Event 생성"""
        category = next((c for c in user_categories if str(c.id) == result.get("category")), None)
        if not category:
            raise CustomException(status_code=status.HTTP_400_BAD_REQUEST, detail="유효하지 않은 카테고리입니다")

        event = event_models.Event(
            name=result.get("name", ""),
            location=result.get("location"),
            start_date=date.fromisoformat(result["startDate"]),
            end_date=date.fromisoformat(result["endDate"]),
            start_time=time.fromisoformat(result["startTime"]) if result.get("startTime") else None,
            end_time=time.fromisoformat(result["endTime"]) if result.get("endTime") else None,
            visibility=Visibility.PRIVATE,
            source_text=source_text
        )

        event_crud.save(self.db, event)

        participant = participant_models.Participant(
            user_id=user.id,
            event_id=event.id,
            category_id=category.id,
            role="OWNER",
            status="ACCEPTED"
        )

        participant_crud.save(self.db, participant)

        alert = alert_models.Alert(
            participant_id=participant.id,
            type="EVENT_START",
            minutes_before=0
        )

        alert_crud.save(self.db, alert)

        return AIEventResponse(
            id=event.id,
            name=event.name,
            location=event.location,
            start_date=event.start_date,
            end_date=event.end_date,
            start_time=event.start_time,
            end_time=event.end_time,
            visibility=event.visibility.value,
            source_text=event.source_text,
            color=category.color
        )

    def _create_task_from_parsed_result(
        self, 
        result: Dict[str, Any], 
        user: user_models.User, 
        user_categories: List, 
        source_text: str
    ) -> AITaskResponse:
        """파싱된 결과로부터 Task 생성"""
        category = next((c for c in user_categories if str(c.id) == result.get("category")), None)
        if not category:
            raise CustomException(status_code=status.HTTP_400_BAD_REQUEST, detail="유효하지 않은 카테고리입니다")

        task = task_models.Task(
            name=result.get("name", ""),
            location=result.get("location"),
            start_time=datetime.fromisoformat(result["startTime"]) if result.get("startTime") else None,
            end_time=datetime.fromisoformat(result["endTime"]) if result.get("endTime") else None,
            scheduled_time=datetime.fromisoformat(result["scheduledTime"]) if result.get("scheduledTime") else None,
            is_completed=False,
            visibility=Visibility.PRIVATE,
            source_text=source_text
        )

        task_crud.save(self.db, task)

        participant = participant_models.Participant(
            user_id=user.id,
            task_id=task.id,
            category_id=category.id,
            role="OWNER",
            status="ACCEPTED"
        )

        participant_crud.save(self.db, participant)

        if result.get("scheduledTime"):
            alert = alert_models.Alert(
                participant_id=participant.id,
                type="TASK_SCHEDULE",
                minutes_before=0
            )
            alert_crud.save(self.db, alert)

        return AITaskResponse(
            id=task.id,
            name=task.name,
            location=task.location,
            start_time=task.start_time,
            end_time=task.end_time,
            scheduled_time=task.scheduled_time,
            is_completed=task.is_completed,
            visibility=task.visibility.value,
            source_text=task.source_text,
            color=category.color
        )

    def _parse_text_with_ai(self, text: str, categories: List[CategoryInfo]) -> Dict[str, Any]:
        """AI를 사용하여 텍스트 파싱"""
        if not self.client:
            raise CustomException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="AI 서비스가 설정되지 않았습니다")

        today = date.today()
        categories_json = json.dumps([{"id": c.id, "name": c.name} for c in categories], ensure_ascii=False)

        prompt_template = """
# 페르소나
너는 사용자가 입력한 한 줄의 텍스트를 분석해서, 그 의도를 파악하고 'EVENT' 또는 'TASK'로 분류한 뒤, 완벽한 JSON 데이터를 생성하는 AI 시간 관리 비서야.

# 입력 텍스트
{text}

# 핵심 원칙: EVENT vs TASK 구분 철학
너의 가장 중요한 임무는 'EVENT'와 'TASK'를 명확히 구분하는 것이다.
- **EVENT**: '시간의 점유'에 초점을 맞춘다. 사용자가 특정 시간(예: "저녁 9시")을 어떤 활동으로 '보내기로' 확정한 경우다. 약속, 회의, 예약 등이 해당한다. **"내일 저녁 9시 운동"은 9시라는 시간을 점유하므로 EVENT다.**
- **TASK**: '결과의 완수'에 초점을 맞춘다. 특정 시점까지(예: "내일까지") 어떤 행동을 '완료해야' 하는 경우다. 제출, 구매, 연락 등이 해당한다. **"내일까지 운동하기"는 완료가 중요하므로 TASK다.**

# 데이터 필드 명세
오늘 날짜의 기준은 {today} 이다. 사용자가 날짜를 지정한 경우(예: '15일', '다음주 월요일')에는 그 날짜를 우선적으로 해석한다. 날짜 정보가 명확하지 않고 기간으로 해석될 여지가 있을 때만 이 기준을 사용해서 추론하라.

## 공통 필드
- **type (필수)**: 위의 철학에 따라 'EVENT' 또는 'TASK' 중 하나를 결정한다.
- **name (필수)**: 일정의 제목을 간결하게 요약한다.
- **location**: 장소 정보가 있다면 포함한다.
- **category (필수)**: 아래 주어진 카테고리 목록 중 가장 적합한 것의 `id` 값을 문자열로 반환한다.
    {categories}

## type이 EVENT일 경우
- **startDate (필수)**: 이벤트 시작 날짜. `yyyy-MM-dd` 형식.
- **endDate (필수)**: 이벤트 종료 날짜. `yyyy-MM-dd` 형식.
- **startTime**: 이벤트 시작 시간. `HH:mm:ss` 형식. 시간이 명시되지 않았다면 null.
- **endTime**: 이벤트 종료 시간. `HH:mm:ss` 형식. 종료 시간이 명시되지 않았다면 null.

## type이 TASK일 경우
- **startTime**: 할 일을 시작할 수 있는 기간의 시작. `yyyy-MM-dd'T'HH:mm:ss` 형식. 시작 시간이 명시되지 않았다면 null.
- **endTime**: 할 일을 완료해야 하는 마감 기한. `yyyy-MM-dd'T'HH:mm:ss` 형식. 마감 기한이 명시되지 않았다면 null.
- **scheduledTime**: 사용자가 이 할 일을 하기로 계획한 특정 시간. `yyyy-MM-dd'T'HH:mm:ss` 형식. 정확히 어떤 시간에 할지 명확하지 않다면 null 무조건.
- startTime <= scheduledTime <= endTime 을 만족해야 한다.
- scheduledTime은 현재 시각 이후여야 한다.

# 응답 형식
반드시 아래 예시처럼 JSON 객체 하나만 응답해야 한다. JSON 이외의 설명, 안내, 텍스트, 마크다운 기호 등은 절대 포함하지 마라.
```json
{{
  "type": "EVENT",
  "name": "팀 회의",
  "location": "강남역 10번 출구",
  "category": "123",
  "startDate": "2024-05-21",
  "endDate": "2024-05-21",
  "startTime": "15:00:00",
  "endTime": "16:30:00"
}}
```
"""

        prompt = prompt_template.format(
            text=text, 
            today=today.strftime("%Y-%m-%d"),
            categories=categories_json
        )

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                generation_config={
                    "temperature": 0.2,
                }
            )
            raw_response = response.text

            # JSON 추출
            start_idx = raw_response.find('{')
            end_idx = raw_response.rfind('}')
            
            if start_idx == -1 or end_idx == -1:
                raise ValueError("JSON not found in response")
                
            json_response = raw_response[start_idx:end_idx + 1]
            
            return json.loads(json_response)

        except Exception as e:
            print(f"AI parsing error: {e}")
            raise CustomException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="텍스트 분석 중 오류가 발생했습니다")
