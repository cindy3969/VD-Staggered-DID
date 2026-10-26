"""Export user-visible local VD conversations, without internal reasoning or credentials."""
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home() / '.codex'
OUT = ROOT / 'chatgpt_history'
OUT.mkdir(exist_ok=True)
state = sqlite3.connect(f'file:{HOME.as_posix()}/state_5.sqlite?mode=ro', uri=True)
history = sqlite3.connect(f'file:{HOME.as_posix()}/thread_history_1.sqlite?mode=ro', uri=True)
titles = {}
for line in (HOME / 'session_index.jsonl').read_text(encoding='utf-8').splitlines():
    try:
        entry = json.loads(line)
        titles[entry['id']] = entry.get('thread_name', '')
    except (ValueError, KeyError):
        pass
index = []
for tid, title, cwd, source in state.execute('select id,title,cwd,source from threads'):
    if cwd.removeprefix('\\\\?\\').rstrip('\\/').lower() != str(ROOT).lower() or 'subagent' in source:
        continue
    title = titles.get(tid) or title.splitlines()[0][:120]
    messages = []
    for ordinal, data in history.execute("select rollout_ordinal,item_json from thread_items where thread_id=? and item_type in ('userMessage','agentMessage') order by rollout_ordinal", (tid,)):
        item = json.loads(data)
        messages.append({'ordinal': ordinal, 'message': item})
    (OUT / f'{tid}.json').write_text(json.dumps({'id':tid,'title':title,'messages':messages},ensure_ascii=False,indent=2),encoding='utf-8')
    blocks = [f'# {title}', f'Chat ID: {tid}', 'Exported: 2026-10-26 (Asia/Seoul). User and assistant messages; internal reasoning and tool logs excluded.']
    for row in messages:
        item=row['message']
        text=item.get('text') or '\n'.join(x.get('text','') if x.get('type')=='text' else json.dumps(x,ensure_ascii=False) for x in item.get('content',[]))
        blocks.append(f"## {'User' if item['type']=='userMessage' else 'Assistant'}\n\n{text}")
    (OUT / f'{tid}.md').write_text('\n\n'.join(blocks)+'\n',encoding='utf-8')
    index.append({'id':tid,'title':title,'messages':len(messages)})
(OUT / 'index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT / 'README.md').write_text('# VD chat history\n\nLocal VD project conversations exported on 2026-10-26. These are readable archives, not a live ChatGPT project. External attachments are referenced, not copied unless already in the VD folder. Cloud-only ChatGPT conversations are not included in this local export.\n\n'+'\n'.join(f"- [{r['title']}]({r['id']}.md) ({r['messages']} messages)" for r in index)+'\n',encoding='utf-8')
print(json.dumps({'chats':len(index),'messages':sum(r['messages'] for r in index)}))
