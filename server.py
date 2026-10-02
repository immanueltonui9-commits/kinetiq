#!/usr/bin/env python3
import csv, json, os, re
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
DATA.mkdir(exist_ok=True)
WAITLIST = DATA / 'waitlist.csv'

if not WAITLIST.exists():
    with WAITLIST.open('w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(['timestamp_utc','name','email','company','workflow'])

EMAIL_RE = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')

def add_signup(row):
    with WAITLIST.open('a', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(row)

def email_exists(email):
    with WAITLIST.open('r', newline='', encoding='utf-8') as f:
        return any(r.get('email','').lower() == email.lower() for r in csv.DictReader(f))

class Handler(BaseHTTPRequestHandler):
    def _json(self, code, payload):
        raw = json.dumps(payload).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers(); self.wfile.write(raw)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ('/','/index.html'):
            raw = (ROOT/'index.html').read_bytes()
            self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw); return
        if path == '/health': self._json(200, {'ok':True}); return
        if path == '/admin/waitlist-count':
            with WAITLIST.open('r', encoding='utf-8') as f: count=max(sum(1 for _ in f)-1,0)
            self._json(200, {'count':count}); return
        self._json(404, {'error':'Not found'})

    def do_POST(self):
        path = urlparse(self.path).path
        if path != '/api/waitlist': self._json(404, {'error':'Not found'}); return
        try:
            length = int(self.headers.get('Content-Length','0'))
            if length > 12000: self._json(413, {'error':'Request too large'}); return
            body = json.loads(self.rfile.read(length) or '{}')
            name = str(body.get('name','')).strip()
            email = str(body.get('email','')).strip()
            company = str(body.get('company','')).strip()
            workflow = str(body.get('workflow','')).strip()
            if not name or len(name)>80: raise ValueError('Please enter your name.')
            if not EMAIL_RE.match(email) or len(email)>160: raise ValueError('Please enter a valid email.')
            if not workflow or len(workflow)>800: raise ValueError('Please describe what you want to automate.')
            if len(company)>120: raise ValueError('Company name is too long.')
            if email_exists(email): self._json(200, {'ok':True, 'duplicate':True}); return
            add_signup([datetime.now(timezone.utc).isoformat(),name,email,company,workflow])
            self._json(201, {'ok':True})
        except json.JSONDecodeError:
            self._json(400, {'error':'Invalid request.'})
        except ValueError as exc:
            self._json(400, {'error':str(exc)})
        except Exception:
            self._json(500, {'error':'Could not save signup.'})

    def log_message(self, fmt, *args):
        print('%s - %s' % (self.address_string(), fmt % args))

if __name__ == '__main__':
    port = int(os.environ.get('PORT','8000'))
    print(f'Kinetiq landing page running at http://localhost:{port}')
    ThreadingHTTPServer(('0.0.0.0',port), Handler).serve_forever()
