"""
前端启动脚本
双击或运行此文件即可启动前端服务
"""
import http.server
import socketserver
import os
import webbrowser

PORT = 8080

if __name__ == "__main__":
    # 切换到 frontend 目录（确保脚本在任意位置运行都能找到文件）
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("localhost", PORT), handler) as httpd:
        print("正在启动前端服务...")
        print(f"前端地址: http://localhost:{PORT}")
        print("按 Ctrl+C 停止服务")
        # 自动打开浏览器
        webbrowser.open(f"http://localhost:{PORT}")
        httpd.serve_forever()
