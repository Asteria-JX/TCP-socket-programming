import socket
import json
import select
import threading
from concurrent.futures import ThreadPoolExecutor

# 服务器设置
SERVER_PORT = 4216
BUFFER_SIZE = 1024
THREAD_POOL_SIZE = 10  # 线程池大小

# 创建套接字
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 允许套接字地址的重用
server_socket.bind(('', SERVER_PORT))  # 绑定到服务器端口
server_socket.listen(5)  # 开始监听连接

# 创建线程池，用于处理客户端连接
executor = ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE)

# 存储客户端套接字的字典
client_sockets = {}

# 自定义异常类，用于处理客户端连接中断
class ConnectionAbortedError(Exception):
    pass


# 处理客户端连接的函数
def handle_client(client_socket):
    try:
        while True:
            # 尝试接收客户端发来的数据
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                # 客户端断开连接：
                # raise ConnectionAbortedError()
                break
            # 解析JSON格式报文
            msg = json.loads(data.decode('utf-8'))
            msg_type = msg.get('Type')
            # 根据消息类型进行处理
            if msg_type == 1:  # Iinitializaiton
                # 处理初始化报文
                N = msg["N"]
                print(f"Received initialization message, block count N={N}")
                # 发送同意报文
                response = {
                    'Type': 2
                }  # agree message
                client_socket.sendall(json.dumps(response).encode('utf-8'))
            elif msg_type == 3:  # reverseRequest
                # 处理reverse请求
                data = msg.get('Data')
                reversed_data = data[::-1]
                reversed_len = len(reversed_data)
                # 构造reverseAnswer报文
                response = {
                    'Type': 4,
                    'Length': reversed_len,
                    'reverseData': reversed_data
                }  # reversedAnswer
                client_socket.sendall(json.dumps(response).encode('utf-8'))
                print(f"Sending reversed data to {client_sockets[client_socket]} : {reversed_data}")
    except ConnectionAbortedError as e:
        pass
    except json.JSONDecodeError:
        print("Received message with incorrect JSON format")
    finally:
        # 关闭客户端套接字
        client_socket.close()
        # 从客户端套接字字典中移除客户端套接字
        if client_socket in client_sockets:
            client_sockets.pop(client_socket)


# 服务器主函数，负责监控活动套接字
def server(stop_event):
    global client_sockets
    while not stop_event.is_set():
        try:
            # 增加超时时间，这里设置为0.5秒
            readable, writable, exceptional = select.select(client_sockets, [], [], 0.5)
        except ValueError as e:
            # print(f"select.select() raised an error: {e}")
            continue

        # 处理可读套接字
        for sock in readable:
            if sock in client_sockets:
                executor.submit(handle_client, sock)  # 使用线程池处理客户端连接
            else:
                print("Client disconnected gracefully")
                continue
                # print("Error:sock not found in client_sockets")

        # 处理异常套接字
        for sock in exceptional:
            if sock in client_sockets:
                client_sockets.pop(sock)
                print("Exception with client socket, disconnected")
                sock.close()

    print("Cleaning up...")
    # 清理资源
    for sock in client_sockets:
        sock.close()
    server_socket.close()
    print("Server has been stopped.")


# 监控命令行输入，用于停止服务器
def monitor_input(stop_event):
    while not stop_event.is_set():
        command = input(f"Enter 'end' to stop the server \n")
        if command.strip().lower() == 'end':
            stop_event.set()
            print("Server is shutting down...")


# 接受新连接的函数
def accept_connections():
    global client_sockets
    while True:
        try:
            client_socket, addr = server_socket.accept()
            print(f"New connection from {addr}")
            client_sockets[client_socket] = addr  # 将新连接的客户端套接字添加到字典中
        except socket.error as e:
            print(f"Failed to accept new connection: {e}")


# 主函数
if __name__ == "__main__":
    print(f"TCP server is listening on Port: {SERVER_PORT}")
    stop_event = threading.Event()

    # 创建并启动服务器接收连接的线程
    accept_thread = threading.Thread(target=accept_connections, daemon=True)
    accept_thread.start()

    # 创建并启动服务器线程
    server_thread = threading.Thread(target=server, args=(stop_event,), daemon=True)
    server_thread.start()

    # 在单独的线程中监控命令行输入
    threading.Thread(target=monitor_input, args=(stop_event,), daemon=True).start()

    # 等待服务器线程结束
    server_thread.join()
