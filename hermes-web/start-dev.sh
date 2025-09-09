#!/bin/bash

echo "🚀 Starting ZSCE Agent Web Application Development Environment..."

# 检查是否在正确的目录
if [ ! -f "start-dev.sh" ]; then
    echo "❌ Error: Please run this script from the zswe-agent-web directory"
    exit 1
fi

# 启动后端服务
echo "🔧 Starting FastAPI backend..."
cd backend
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

echo "🔑 Activating virtual environment..."
source .venv/bin/activate

echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo "🚀 Starting FastAPI server on http://localhost:8000..."
echo "📚 API documentation will be available at http://localhost:8000/docs"
echo ""

# 在后台启动后端服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端服务
echo "🎨 Starting Next.js frontend..."
cd ../frontend

echo "📥 Installing dependencies..."
npm install

echo "🚀 Starting Next.js development server on http://localhost:3000..."
echo ""

# 启动前端服务
npm run dev &
FRONTEND_PID=$!

echo "✅ Development environment started successfully!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# 等待用户中断
trap "echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# 保持脚本运行
wait
