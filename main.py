with open('requirements.txt', 'w') as f:
    f.write("fastapi\nuvicorn\npydantic\n")

fixed_todo_content = """from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TodoManager:
    def __init__(self):
        self.todos = [
            {"id": 1, "title": "파이썬 공부하기", "deadline": "2026-07-10", "completed": False},
            {"id": 2, "title": "방 청소하기", "deadline": "2026-07-05", "completed": True}
        ]
        self.current_id = 3

    def get_all(self):
        return self.todos

    def add_item(self, title: str, deadline: str):
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
                return {"status": "성공", "message": "상태 변경 완료"}
        return {"status": "실패", "message": "찾을 수 없음"}

    def delete_item(self, todo_id: int):
        for i, todo in enumerate(self.todos):
            if todo["id"] == todo_id:
                self.todos.pop(i)
                return {"status": "성공", "message": "삭제 완료"}
        return {"status": "실패", "message": "찾을 수 없음"}

schedule_system = TodoManager()

class TodoCreate(BaseModel):
    title: str
    deadline: str

@app.get("/", response_class=HTMLResponse)
def read_root():
    # 파이썬과 자바스크립트 간의 따옴표 충돌을 막기 위해 HTML 내부에 템플릿 리터럴(백틱) 사용을 제거했습니다.
    return \"\"\"
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

        <h3 style="margin-bottom: 10px; color: #1f2937; font-size: 16px;">📋 나의 일정 리스트</h3>
        <div id="todoContainer" style="min-height: 50px;"></div>
    </div>

    <script>
        const todoContainer = document.getElementById('todoContainer');

        async function loadTodos() {
            try {
                const response = await fetch('/api/todos');
                const todos = await response.json();
                todoContainer.innerHTML = '';
                
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

                    const titleStyle = item.completed ? 'text-decoration: line-through; color: #9ca3af;' : 'color: #1f2937; font-weight: 500;';
                    
                    // 따옴표 오류 방지를 위해 표준 문자열 결합 형식으로 수정
                    itemDiv.innerHTML = '<div style="display: flex; align-items: center; gap: 10px; flex: 1;">' +
                        '<input type="checkbox" ' + (item.completed ? 'checked' : '') + ' onclick="toggleTodo(' + item.id + ')" style="width: 18px; height: 18px; cursor: pointer;">' +
                        '<div>' +
                            '<div style="' + titleStyle + '">' + item.title + '</div>' +
                            '<div style="font-size: 12px; color: #6b7280; margin-top: 2px;">⏳ 마감: ' + item.deadline + '</div>' +
                        '</div>' +
                    '</div>' +
                    '<button onclick="deleteTodo(' + item.id + ')" style="background: none; border: none; color: #ef4444; cursor: pointer; font-size: 14px; font-weight: bold; padding: 4px 8px;">삭제</button>';
                    
                    todoContainer.appendChild(itemDiv);
                });
            } catch (error) {
                console.error(error);
            }
        }

        document.getElementById('btnAdd').addEventListener('click', async () => {
            const title = document.getElementById('todoTitle').value;
            const deadline = document.getElementById('todoDeadline').value;
            
            if(!title.trim()) {
                alert('할 일 내용을 입력해주세요!');
                return;
            }

            try {
                await fetch('/api/todos', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title: title, deadline: deadline })
                });
                document.getElementById('todoTitle').value = '';
                document.getElementById('todoDeadline').value = '';
                loadTodos();
            } catch (error) {
                alert('통신 에러');
            }
        });

        async function toggleTodo(id) {
            try {
                await fetch('/api/todos/' + id + '/toggle', { method: 'POST' });
                loadTodos();
            } catch (error) {
                alert('변경 실패');
            }
        }

        async function deleteTodo(id) {
            if(!confirm('정말 삭제하시겠습니까?')) return;
            try {
                await fetch('/api/todos/' + id, { method: 'DELETE' });
                loadTodos();
            } catch (error) {
                alert('삭제 실패');
            }
        }

        window.onload = loadTodos;
    </script>
    \"\"\"

@app.get("/api/todos")
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
"""

with open('main.py', 'w') as f:
    f.write(fixed_todo_content)

print("🎉 오류가 수정된 main.py 파일이 새로 생성되었습니다!")
