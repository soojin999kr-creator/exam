from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uvicorn

app = FastAPI()

# Enable CORS for Google Apps Script and other web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define Fixed-Size Queue (고정 길이 큐) Data Structure class
class FixedQueue:
    def __init__(self, capacity: int = 20):
        self.capacity = capacity
        self.que = [None] * capacity
        self.front = 0
        self.rear = 0
        self.no = 0  # Current data count

    def clear(self):
        """1) 초기화 및 6) 큐 전체 데이터 삭제"""
        self.front = self.rear = self.no = 0
        self.que = [None] * self.capacity

    def push(self, value: int) -> int:
        """2) push 연산 (큐에 데이터 삽입)"""
        if self.no >= self.capacity:
            raise Exception("Queue is Full (Overflow)")
        self.que[self.rear] = value
        self.rear = (self.rear + 1) % self.capacity
        self.no += 1
        return value

    def pop(self) -> int:
        """2) pop 연산 (큐의 전면 데이터 추출 및 제거)"""
        if self.no <= 0:
            raise Exception("Queue is Empty (Underflow)")
        val = self.que[self.front]
        self.front = (self.front + 1) % self.capacity
        self.no -= 1
        return val

    def size(self) -> int:
        """3) 현재 데이터 개수(길이/크기) 반환"""
        return self.no

    def is_empty(self) -> bool:
        """4) 상태 검사: 비어있는지 여부"""
        return self.no <= 0

    def is_full(self) -> bool:
        """4) 상태 검사: 가득 찼는지 여부"""
        return self.no >= self.capacity

    def peek(self):
        """5) 전면(Front) 데이터 확인 (삭제하지 않음)"""
        if self.no <= 0:
            return None
        return self.que[self.front]

    def find(self, value: int) -> int:
        """7) 값의 index 검색 (Front부터 탐색하여 몇 번째 인덱스인지 반환, 없으면 -1)"""
        for i in range(self.no):
            idx = (self.front + i) % self.capacity
            if self.que[idx] == value:
                return idx
        return -1

    def count(self, value: int) -> int:
        """8) 값의 개수(길이/크기) 반환"""
        cnt = 0
        for i in range(self.no):
            idx = (self.front + i) % self.capacity
            if self.que[idx] == value:
                cnt += 1
        return cnt

    def contains(self, value: int) -> bool:
        """9) 값의 존재 여부 검사"""
        for i in range(self.no):
            idx = (self.front + i) % self.capacity
            if self.que[idx] == value:
                return True
        return False

    def dump(self) -> list:
        """10) Front부터 Rear까지 출력"""
        result = []
        for i in range(self.no):
            idx = (self.front + i) % self.capacity
            result.append(self.que[idx])
        return result

# Initialize global fixed queue instance with capacity 20
queue = FixedQueue(20)

class QueueRequest(BaseModel):
    action: str
    value: int = None
    values: list[int] = None

@app.get("/")
def read_root():
    return {"status": "running", "message": "Fixed-Size Queue Cloud Run Server is active!"}

@app.post("/queue_ops")
def queue_operations(req: QueueRequest):
    """
    Handles all 10 server functions requested by client.
    """
    try:
        action = req.action
        
        if action == "init":
            queue.clear()
            status_msg = "큐가 초기화되었습니다."
            
        elif action == "push":
            if req.values:
                for v in req.values:
                    queue.push(v)
                status_msg = f"배열 {req.values}이(가) 성공적으로 push되었습니다."
            elif req.value is not None:
                queue.push(req.value)
                status_msg = f"값 {req.value}이(가) push되었습니다."
            else:
                raise HTTPException(status_code=400, detail="Push할 값이 없습니다.")
                
        elif action == "pop":
            val = queue.pop()
            status_msg = f"Pop된 값: {val}"
            
        elif action == "size":
            pass # just return status
            
        elif action == "status":
            pass # return full/empty info
            
        elif action == "peek":
            pass # return front value
            
        elif action == "clear":
            queue.clear()
            status_msg = "큐 전체 데이터가 삭제되었습니다."
            
        elif action == "find":
            idx = queue.find(req.value)
            cnt = queue.count(req.value)
            return {
                "status": "success",
                "message": f"값 {req.value} 검색 완료",
                "index": idx,
                "count": cnt,
                "data": queue.dump(),
                "size": queue.size(),
                "is_full": queue.is_full(),
                "is_empty": queue.is_empty(),
                "front": queue.peek()
            }
            
        elif action == "contains":
            exists = queue.contains(req.value)
            return {
                "status": "success",
                "message": f"값 {req.value} 존재 여부 검사 완료",
                "exists": exists,
                "data": queue.dump(),
                "size": queue.size(),
                "is_full": queue.is_full(),
                "is_empty": queue.is_empty(),
                "front": queue.peek()
            }
            
        elif action == "dump":
            pass
            
        else:
            raise HTTPException(status_code=400, detail="알 수 없는 액션입니다.")

        return {
            "status": "success",
            "message": status_msg if 'status_msg' in locals() else "작업 성공",
            "size": queue.size(),
            "is_full": queue.is_full(),
            "is_empty": queue.is_empty(),
            "front": queue.peek(),
            "data": queue.dump()
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
