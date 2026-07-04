from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AccountManager:
    def __init__(self):
        self.users = {
            "test1": {"pw": "1234", "balance": 5000},
            "test2": {"pw": "5678", "balance": 10000}
        }
    
    def deposit(self, user_id, amount):
        try:
            amount = int(amount)
            if amount <= 0: return "실패: 0원 이하의 금액은 충전할 수 없습니다."
        except ValueError: return "실패: 올바른 금액 형식이 아닙니다."
            
        if user_id in self.users:
            self.users[user_id]["balance"] += amount
            return f"성공: {user_id}님 계좌에 {amount}원이 충전되었습니다. (현재 잔액: {self.users[user_id]['balance']}원)"
        return f"실패: '{user_id}' 데이터가 존재하지 않습니다."

    def register(self, user_id, user_pw):
        if not user_id or not user_pw: return "실패: 데이터 부족"
        if user_id in self.users: return f"실패: '{user_id}'는 이미 존재합니다."
        self.users[user_id] = {"pw": user_pw, "balance": 0}
        return f"성공: '{user_id}'님의 회원가입이 완료되었습니다!"

backend_system = AccountManager()

class RegisterRequest(BaseModel):
    userId: str
    userPw: str

class DepositRequest(BaseModel):
    userId: str
    amount: int

@app.get("/", response_class=HTMLResponse)
def read_root():
    return '''
    <div style="padding: 24px; border: 1px solid #e0e0e0; border-radius: 12px; max-width: 450px; margin: 50px auto; background-color: #ffffff; font-family: sans-serif; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h2 style="margin-top: 0; color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 8px;">실제 배포된 계좌 관리 시스템</h2>
        
        <div style="display: flex; margin-bottom: 20px; background: #f1f3f4; border-radius: 8px; padding: 4px;">
            <button id="tabReg" style="flex: 1; padding: 8px; border: none; background: #ffffff; border-radius: 6px; cursor: pointer; font-weight: bold;">회원가입</button>
            <button id="tabDep" style="flex: 1; padding: 8px; border: none; background: transparent; border-radius: 6px; cursor: pointer; color: #5f6368;">잔액 충전</button>
        </div>
        
        <div style="margin-bottom: 12px;">
            <label style="display: block; margin-bottom: 6px; font-weight: bold;">사용자 ID</label>
            <input type="text" id="userId" style="width: 100%; padding: 10px; box-sizing: border-box;">
        </div>
        
        <div id="dynamicInputGroup" style="margin-bottom: 20px;">
            <label id="dynamicLabel" style="display: block; margin-bottom: 6px; font-weight: bold;">비밀번호</label>
            <input type="password" id="dynamicInput" style="width: 100%; padding: 10px; box-sizing: border-box;">
        </div>
        
        <button id="btnAction" style="width: 100%; padding: 12px; background-color: #1a73e8; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: bold;">회원가입 하기</button>
        
        <div id="statusMessage" style="margin-top: 20px; padding: 12px; background-color: #f8f9fa; border-left: 4px solid #ced4da; border-radius: 4px; font-size: 14px;">
            결과가 여기에 표시됩니다.
        </div>
    </div>

    <script>
        let currentMode = 'register';
        const tabReg = document.getElementById('tabReg');
        const tabDep = document.getElementById('tabDep');
        const dynamicLabel = document.getElementById('dynamicLabel');
        const dynamicInput = document.getElementById('dynamicInput');
        const btnAction = document.getElementById('btnAction');
        const statusMessage = document.getElementById('statusMessage');
        
        tabReg.addEventListener('click', () => { currentMode = 'register'; tabReg.style.background = '#ffffff'; tabDep.style.background = 'transparent'; dynamicLabel.innerText = '비밀번호'; dynamicInput.type = 'password'; btnAction.innerText = '회원가입 하기'; });
        tabDep.addEventListener('click', () => { currentMode = 'deposit'; tabDep.style.background = '#ffffff'; tabReg.style.background = 'transparent'; dynamicLabel.innerText = '충전 금액 (원)'; dynamicInput.type = 'number'; btnAction.innerText = '잔액 충전하기'; });

        btnAction.addEventListener('click', async () => {
            const userId = document.getElementById('userId').value;
            const secondVal = dynamicInput.value;
            statusMessage.innerText = '처리 중...';
            
            let url = currentMode === 'register' ? '/api/register' : '/api/deposit';
            let bodyData = currentMode === 'register' 
                ? JSON.stringify({ userId: userId, userPw: secondVal })
                : JSON.stringify({ userId: userId, amount: parseInt(secondVal) });

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: bodyData
                });
                const resultText = await response.text();
                statusMessage.innerText = resultText;
            } catch (error) {
                statusMessage.innerText = '에러 발생: ' + error;
            }
        });
    </script>
    '''

@app.post("/api/register")
def api_register(data: RegisterRequest):
    return backend_system.register(data.userId, data.userPw)

@app.post("/api/deposit")
def api_deposit(data: DepositRequest):
    return backend_system.deposit(data.userId, data.amount)
