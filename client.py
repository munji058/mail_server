import socket
import json
import threading

def listen_for_mail(sock):
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                break
            res = json.loads(data.decode())
            if res.get("status") == "new_mail":
                mail = res["mail"]
                print(f"\n📬 새 메일 도착! From: {mail['from']} | Subject: {mail['subject']}")
        except Exception as e:
            print(f"[listen_for_mail] 오류: {e}")
            break

def send_cmd(sock, cmd):
    sock.send(json.dumps(cmd).encode())
    response = sock.recv(4096)
    return json.loads(response.decode())

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 9001))

        # 로그인
        print("== Login ==")
        uid = input("ID: ")
        pw = input("PW: ")
        res = send_cmd(s, {"cmd": "login", "id": uid, "pw": pw})
        print("[응답]", res)

        if res.get("status") != "OK":
            print("❌ 로그인 실패")
            exit()

        # 로그인 성공 후 수신 대기 스레드 시작
        threading.Thread(target=listen_for_mail, args=(s,), daemon=True).start()

        # 명령어 루프
        while True:
            cmd = input("\n명령어 (send / list / read / delete / exit): ").strip().lower()

            if cmd == "send":
                to = input("To: ")
                subject = input("Subject: ")
                body = input("Body: ")
                res = send_cmd(s, {"cmd": "send", "to": to, "subject": subject, "body": body})
                print("[Send 응답]", res)

            elif cmd == "list":
                res = send_cmd(s, {"cmd": "list"})
                print("[목록]")
                for m in res.get("mails", []):
                    print(" -", m)

            elif cmd == "read":
                idx = int(input("메일 번호: "))
                res = send_cmd(s, {"cmd": "read", "index": idx})
                if "mail" in res:
                    mail = res["mail"]
                    print(f"From: {mail['from']}\nSubject: {mail['subject']}\nBody: {mail['body']}")
                else:
                    print("[읽기 실패]", res)

            elif cmd == "delete":
                idx = int(input("메일 번호: "))
                res = send_cmd(s, {"cmd": "delete", "index": idx})
                print("[삭제 응답]", res)

            elif cmd == "exit":
                print("종료합니다.")
                break

            else:
                print("지원하지 않는 명령입니다.")
