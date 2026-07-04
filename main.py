from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# CORS 보안 허용 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# 1. 백엔드 데이터 모델 및 데이터베이스 역할 (메모리 저장)
# =====================================================================
class TodoItem(BaseModel):
    id: int
    title: str
    deadline: str
    completed: bool = False

class TodoCreate(BaseModel):
    title: str
    deadline: str

class TodoManager:
    def __init__(self):
        # 기본 예시 데이터
        self.todos = [
            {"id": 1, "title": "파이썬 코딩 공부하기", "deadline": "2026-07-10", "completed": False},
            {"id": 2, "title": "방 청소 및 분리수거", "deadline": "2026-07-05", "completed": True}
        ]
        self.current_id = 3

    def get_all(self):
        return self.todos

    def add_item(self, title: str, deadline: str):
        if not title.strip():
            return {"status": "실패", "message": "할 일 내용을 입력해주세요."}
        
        new_todo = {
            "id": self.current_id,
            "title": title,
            "deadline": deadline if deadline else "기한 없음",
            "completed": False
        }
        self.todos.append(new_todo)
        self.current_id += 1
        return {"status": "성공", "message": f"'{title}' 일정이 추가되었습니다."}

    def toggle_item(self, todo_id: int):
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["completed"] = not todo["completed"]
                status_str = "완료" if todo["completed"] else "미완료"
                return {"status": "성공", "message": f"'{todo['title']}' 상태를 {status_str}로 변경했습니다."}
        return {"status": "실패", "message": "해당 일정을 찾을 수 없습니다."}

    def delete_item(self, todo_id: int):
        for i, todo in enumerate(self.todos):
            if todo["id"] == todo_id:
                deleted = self.todos.pop(i)
                return {"status": "성공", "message": f"'{deleted['title']}' 일정을 삭제했습니다."}
        return {"status": "실패", "message": "해당 일정을 찾을 수 없습니다."}

schedule_system = TodoManager()


# =====================================================================
# 2. API 엔드포인트 (접수 창구)
# =====================================================================
@app.get("/", response_class=HTMLResponse)
def read_root():
    return '''
    <div style="padding: 24px; border: 1px solid #e0e0e0; border-radius: 12px; max-width: 500px; margin: 40px auto; background-color: #ffffff; font-family: sans-serif; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
        <h2 style="margin-top: 0; color: #4f46e5; border-bottom: 2px solid #4f46e5; padding-bottom: 8px; text-align: center;">📅 스마트 스케줄러 (To-Do)</h2>
        
        <div style="background-color: #f9fafb; padding: 16px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #f3f4f6;">
            <div style="margin-bottom: 10px;">
                <label style="display: block; margin-bottom: 4px; font-weight: bold; font-size: 14px; color: #374151;">할 일 목록 추가</label>
                <input type="text" id="todoTitle" placeholder="무엇을 해야 하나요?" style="width: 100%; padding: 10px; box-sizing: border-box; border: 1px solid #d1d5db; border-radius: 6px;">
            </div>
            <div style="margin-bottom: 12px;">
                <label style="display: block; margin-bottom: 4px; font-weight: bold; font-size: 14px; color: #374151;">마감 기한</label>
                <input type="date" id="todoDeadline" style="width: 100%; padding: 10px; box-sizing: border-box; border: 1px solid #d1d5db; border-radius: 6px;">
            </div>
            <button id="btnAdd" style="width: 100%; padding: 12px; background-color: #4f46e5; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 15px; font-weight: bold;">추가하기</button>
        </div>

        <div id="alertMessage" style="display:none; margin-bottom: 15px; padding: 10px; border-left: 4px solid #ced4da; background-color: #f3f4f6; font-size: 13px; border-radius: 4px;"></div>

        <h3 style="margin-bottom: 10px; color: #1f2937; font-size: 16px;">📋 나의 일정 리스트</h3>
        <div id="todoContainer" style="min-height: 50px;">
            </div>
    </div>

    <script>
        const alertMessage = document.getElementById('alertMessage');
        const todoContainer = document.getElementById('todoContainer');

        // 시스템 알림 표시 함수
        function showAlert(msg, isSuccess = true) {
            alertMessage.style.display = 'block';
            alertMessage.innerText = msg;
            alertMessage.style.borderLeftColor = isSuccess ? '#10b981' : '#ef4444';
            setTimeout(() => { alertMessage.style.display = 'none'; }, 3000);
        }

        # [백엔드 통신] 1. 전체 할 일 리스트 가져와서 화면에 그리기
        async function loadTodos() {
            try {
                const response = await fetch('/api/todos');
                const todos = await response.json();
                
                todoContainer.innerHTML = ''; // 기존 목록 비우기
                
                if(todos.length === 0) {
                    todoContainer.innerHTML = '<p style="color:#9ca3af; text-align:center; font-size:14px;">등록된 일정이 없습니다.</p>';
                    return;
                }

                todos.forEach(item => {
                    const itemDiv = document.createElement('div');
                    itemDiv.style.display = 'flex';
                    itemDiv.style.alignItems = 'center';
                    itemDiv.style.justifyContent = 'space-between';
                    itemDiv.style.padding = '12px';
                    itemDiv.style.marginBottom = '8px';
                    itemDiv.style.border = '1px solid #e5e7eb';
                    itemDiv.style.borderRadius = '6px';
                    itemDiv.style.backgroundColor = item.completed ? '#f3f4f6' : '#ffffff';

                    // 완료된 항목은 취소선 처리
                    const titleStyle = item.completed ? 'text-decoration: line-through; color: #9ca3af;' : 'color: #1f2937; font-weight: 500;';
                    
                    itemDiv.innerHTML = `
                        <div style="display: flex; align-items: center; gap: 10px; flex: 1;">
                            <input type="checkbox" ${item.completed ? 'checked' : ''} onclick="toggleTodo(${item.id})" style="width: 18px; height: 18px; cursor: pointer;">
                            <div>
                                <div style="${titleStyle}">${item.title}</div>
                                <div style="font-size: 12px; color: #6b7280; margin-top: 2px;">⏳ 마감: ${item.deadline}</div>
                            </div>
                        </div>
                        <button onclick="deleteTodo(${item.id})" style="background: none; border: none; color: #ef4444; cursor: pointer; font-size: 14px; font-weight: bold; padding: 4px 8px;">삭제</button>
                    `;
                    todoContainer.appendChild(itemDiv);
                });
            } catch (error) {
                console.error('로딩 실패:', error);
            }
        }

        # [백엔드 통신] 2. 새로운 할 일 등록하기
        document.getElementById('btnAdd').addEventListener('click', async () => {
            const title = document.getElementById('todoTitle').value;
            const deadline = document.getElementById('todoDeadline').value;
            
            if(!title.trim()) {
                alert('할 일 내용을 입력해주세요!');
                return;
            }

            try {
                const response = await fetch('/api/todos', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title: title, deadline: deadline })
                });
                const result = await response.json();
                
                if(result.status === '성공') {
                    document.getElementById('todoTitle').value = ''; // 입력창 초기화
                    document.getElementById('todoDeadline').value = '';
                    showAlert(result.message, true);
                    loadTodos(); // 목록 새로고침
                } else {
                    showAlert(result.message, false);
                }
            } catch (error) {
                showAlert('서버 통신 에러', false);
            }
        });

        # [백엔드 통신] 3. 완료 체크박스 토글하기
        async function toggleTodo(id) {
            try {
                const response = await fetch(`/api/todos/${id}/toggle`, { method: 'POST' });
                const result = await response.json();
                showAlert(result.message, result.status === '성공');
                loadTodos();
            } catch (error) {
                showAlert('상태 변경 실패', false);
            }
        }

        # [백엔드 통신] 4. 일정 삭제하기
        async function deleteTodo(id) {
            if(!confirm('정말 이 일정을 삭제하시겠습니까?')) return;
            try {
                const response = await fetch(`/api/todos/${id}`, { method: 'DELETE' });
                const result = await response.json();
                showAlert(result.message, result.status === '성공');
                loadTodos();
            } catch (error) {
                showAlert('삭제 실패', false);
            }
        }

        // 페이지 최초 로딩 시 데이터 불러오기
        window.onload = loadTodos;
    </script>
    '''

@app.get("/api/todos", response_model=List[TodoItem])
def get_todos():
    return schedule_system.get_all()

@app.post("/api/todos")
def create_todo(data: TodoCreate):
    return schedule_system.add_item(data.title, data.deadline)

@app.post("/api/todos/{todo_id}/toggle")
def toggle_todo(todo_id: int):
    return schedule_system.toggle_item(todo_id)

@app.delete("/api/todos/{todo_id}")
def delete_todo(todo_id: int):
    return schedule_system.delete_item(todo_id)
