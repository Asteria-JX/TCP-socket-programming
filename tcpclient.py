import socket
import json
import sys
import random

# 客户端设置
SERVER_IP = sys.argv[1]
SERVER_PORT = int(sys.argv[2])
FILE_PATH = sys.argv[3]
Lmin = int(sys.argv[4])
Lmax = int(sys.argv[5])
BUFFER_SIZE = 1024

addr = (SERVER_IP, SERVER_PORT)  # 服务器地址

# 创建TCP套接字
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# IP地址是否有效
def is_valid_ip(server_ip):
    try:
        socket.inet_aton(server_ip)  # 尝试将字符串ip转换为网格格式
        return True
    except socket.error:
        return False


# 检查Lmin和Lmax是否为有效的长度参数
def are_valid_lengths(Lmin, Lmax):
    return isinstance(Lmin, int) and isinstance(Lmax, int) and 0 < Lmin < Lmax


# 发送JSON报文的函数
def send_msg(sock, msg_type, **kwargs):
    msg = {
        'Type': msg_type,
        **kwargs  # 将额外的关键字参数添加到消息字典中
    }
    sock.sendall(json.dumps(msg).encode('utf-8'))  # 发送JSON格式的字符串


# 接收并解析JSON报文的函数
def receive_msg(sock):
    try:
        data = sock.recv(BUFFER_SIZE)  # 接收数据
        if not data:
            return None
        return json.loads(data.decode('utf-8'))  # 解析JSON格式的字符串
    except json.JSONDecodeError:
        print("Received message with incorrect JSON format")
        return None


# 计算文件块
def calculate_block(total_length):
    blocks = []
    remaining_length = total_length
    while remaining_length > 0:
        block_size = random.randint(Lmin, Lmax)  # 随机选择块大小
        block_size = min(block_size, remaining_length)  # 确保不超过剩余长度
        blocks.append(block_size)
        remaining_length -= block_size
    return blocks


# 客户端主逻辑
def client():
    global client_socket, FILE_PATH
    client_socket.connect(addr)  # 连接到服务器

    with open(FILE_PATH, 'r') as file:
        content = file.read()

    total_length = len(content)  # 获取文件总长度
    block_sizes = calculate_block(total_length)  # 计算块大小

    send_msg(client_socket, 1, N=len(block_sizes))  # 发送初始化报文
    response = receive_msg(client_socket)
    if response and response['Type'] == 2:
        print("Server agreed to the initialization!")
        reversed_content = ""
        index = 0
        for size in block_sizes:
            next_ACK = input("Continue with the next block? (y/n): ")  # 请求用户确认发送下一个块
            if next_ACK == "y":
                block = content[index:index + size]
                if block:
                    send_msg(client_socket, 3, Length=size, Data=block)  # 发送数据块
                    response = receive_msg(client_socket)
                    if response and response['Type'] == 4:
                        reversed_content = response['reverseData'] + reversed_content
                        print(f"Received reversed data block: {response['reverseData']}")
                    else:
                        print("Error receiving reversed data block.")
                        break
                    index += size
                else:
                    print("No more data to send.")

        # 保存反转后的内容到文件
        with open('reversed_content.txt', 'w') as reversed_file:
            reversed_file.write(reversed_content)
        print("Reversed content has been saved to 'reversed_content.txt'.")
    else:
        print("Server did not agree to the initialization.")
        return

    # 关闭套接字
    client_socket.close()


if __name__ == "__main__":
    # 参数个数检查
    if len(sys.argv) != 6:
        print("Please input: python tcpclient.py <server_ip> <server_port> <file_path> <Lmin> <Lmax>")
        sys.exit(1)

    # IP地址有效性检查
    if not is_valid_ip(SERVER_IP):
        print(f"Error: {SERVER_IP} is not a valid IP address.")
        sys.exit(1)

    # Lmin和Lmax有效性检查
    if not are_valid_lengths(Lmin, Lmax):
        print("Error: Lmin and Lmax must be positive integers with Lmin <= Lmax.")
        sys.exit(1)

    # 检查文件是否存在
    try:
        with open(FILE_PATH, 'r') as file:
            pass
    except FileNotFoundError:
        print(f"Error: The file {FILE_PATH} does not exist.")
        sys.exit(1)

    client()  # 执行客户端逻辑
