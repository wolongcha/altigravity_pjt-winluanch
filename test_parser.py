import os
import json
import re
import datetime

def get_sessions(brain_dir=r'C:\Users\aceyo\.gemini\antigravity-cli\brain'):
    sessions = []
    if not os.path.exists(brain_dir):
        return sessions

    for folder in os.listdir(brain_dir):
        folder_path = os.path.join(brain_dir, folder)
        if not os.path.isdir(folder_path):
            continue
        
        t_file = os.path.join(folder_path, '.system_generated', 'logs', 'transcript.jsonl')
        mtime = os.path.getmtime(folder_path)
        if os.path.exists(t_file):
            mtime = os.path.getmtime(t_file)
        
        mtime_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        title = '(대화 기록 없음)'
        msg_count = 0
        user_prompts = []

        if os.path.exists(t_file):
            try:
                with open(t_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if not line.strip():
                            continue
                        msg_count += 1
                        data = json.loads(line)
                        if data.get('type') == 'USER_INPUT':
                            raw_content = data.get('content', '')
                            match = re.search(r'<USER_REQUEST>\s*(.*?)\s*</USER_REQUEST>', raw_content, re.DOTALL)
                            if match:
                                req_text = match.group(1).strip()
                            else:
                                req_text = raw_content.strip()
                            
                            req_text = ' '.join(req_text.splitlines())
                            user_prompts.append(req_text)
                            if title == '(대화 기록 없음)' and req_text:
                                title = req_text
            except Exception as e:
                title = f'오류: {e}'

        sessions.append({
            'id': folder,
            'title': title[:100] if title else '새 세션',
            'mtime': mtime,
            'mtime_str': mtime_str,
            'msg_count': msg_count,
            'prompt_count': len(user_prompts),
            'first_prompt': user_prompts[0] if user_prompts else '',
            'folder_path': folder_path
        })

    sessions.sort(key=lambda x: x['mtime'], reverse=True)
    return sessions

if __name__ == '__main__':
    sess_list = get_sessions()
    print(f"Total Sessions Found: {len(sess_list)}")
    for s in sess_list:
        print(f"[{s['mtime_str']}] {s['id'][:8]}... | Prompt Count: {s['prompt_count']} | Title: {s['title']}")
