"""
后端启动脚本
双击或运行此文件即可启动后端服务
"""
import uvicorn

if __name__ == "__main__":
    print("正在启动后端服务...")
    print("后端地址: http://localhost:3000")
    print("API文档: http://localhost:3000/docs")
    print("按 Ctrl+C 停止服务")
    uvicorn.run("main:app", host="localhost", port=3000, reload=True)
