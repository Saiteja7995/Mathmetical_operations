#updated
from http.server import HTTPServer, BaseHTTPRequestHandler
import re
import json
from collections import deque

host = "127.0.0.1"
port = 3000
history = deque(maxlen=20)

class NHTTP(BaseHTTPRequestHandler):
    def do_GET(self):
        global history
        
        if self.path == "/history":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            history_html = "<html><body><h1>History</h1><ul>"
            for entry in history:
                history_html += f"<li>{entry['question']} = {entry['answer']}</li>"
            history_html += "</ul></body></html>"

            self.wfile.write(history_html.encode("utf-8"))
        else:
            path_pattern = r'^/(\d+)(/(plus|minus|into|divide)/(\d+))*$'
            match = re.match(path_pattern, self.path)

            if match:
                nums = [int(match.group(1))]
                operations = match.groups()[2::4]
                operands = list(map(int, match.groups()[3::4]))

                question = str(nums[0])
                for i, operation in enumerate(operations):
                    if operation == "plus":
                        nums[-1] += operands[i]
                        question += f"+{operands[i]}"
                    elif operation == "minus":
                        nums[-1] -= operands[i]
                        question += f"-{operands[i]}"
                    elif operation == "into":
                        nums[-1] *= operands[i]
                        question += f"*{operands[i]}"
                    elif operation == "divide":
                        nums[-1] /= operands[i]
                        question += f"/{operands[i]}"

                answer = nums[-1]
                history.append({"question": question, "answer": answer})

                response_data = {
                    "question": question,
                    "answer": answer
                }

                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()

                response_json = json.dumps(response_data)
                self.wfile.write(response_json.encode("utf-8"))
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"Invalid URL")

server = HTTPServer((host, port), NHTTP)
print("Server is now listening............")
server.serve_forever()
