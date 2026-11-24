import streamlit as st
import sqlite3, uuid, secrets, string, os, hashlib, hmac, time
import calendar as _calendar, html as _html
from datetime import datetime, date, timedelta
from pathlib import Path
import pandas as pd
import plotly.express as px

APP_DIR=Path(__file__).parent
DB_PATH=APP_DIR/'nexora.db'

st.set_page_config(page_title='NEXORA | Campus OS', page_icon='✦', layout='wide', initial_sidebar_state='expanded')

# ---------- Visual system ----------
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
:root{--bg:#080d18;--panel:#101a2b;--panel2:#14223a;--line:#263b5b;--blue:#4169e1;--royal:#3158c9;--gold:#d6ad55;--muted:#91a2bd;--white:#edf3ff;}
html,body,[class*="css"]{font-family:'Manrope',sans-serif;color:var(--white)}
.stApp{background:radial-gradient(ellipse at 75% -10%,#1b3158 0%,#0b1425 38%,#080d18 75%)}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0c1526,#080e1a);border-right:1px solid #243654}
section[data-testid="stSidebar"] *{color:#dce6fa}
.block-container{padding-top:1.4rem;padding-bottom:3rem;max-width:1600px}
[data-testid="stMetric"]{background:linear-gradient(145deg,#14233b,#0e1829);border:1px solid #2b4164;border-radius:15px;padding:16px 18px;box-shadow:0 8px 28px #0003}
[data-testid="stMetricLabel"]{color:#a8b9d4!important;font-size:.78rem}
[data-testid="stMetricValue"]{color:#f5f7ff!important;font-weight:800}
.stButton>button{border-radius:10px;border:1px solid #4967a0;background:linear-gradient(135deg,#3158c9,#24449f);color:white;font-weight:700;min-height:2.55rem;transition:.2s}
.stButton>button:hover{border-color:#e0bd6b;color:white;box-shadow:0 0 0 2px #d6ad5530}
.stTextInput input,.stTextArea textarea,.stNumberInput input,.stDateInput input,.stTimeInput input,.stSelectbox div[data-baseweb="select"]>div,.stMultiSelect div[data-baseweb="select"]>div{background:#0c1728!important;color:#edf3ff!important;border-color:#30476a!important;border-radius:9px}
label,.stMarkdown p,.stMarkdown li{color:#c7d3e7}
h1,h2,h3{color:#f2f5ff!important;letter-spacing:-.035em}
h1{font-weight:800} h2{font-weight:800} h3{font-weight:700}
hr{border-color:#263b5b}
[data-testid="stDataFrame"]{border:1px solid #2b4164;border-radius:12px;overflow:hidden}
div[data-testid="stAlert"]{border-radius:12px}
.nx-brand{display:flex;align-items:center;gap:12px;padding:9px 4px 20px;border-bottom:1px solid #253957;margin-bottom:20px}
.nx-mark{width:42px;height:42px;border:1px solid #d6ad55;border-radius:12px;display:grid;place-items:center;color:#e3bd69;font-size:22px;background:linear-gradient(145deg,#233b70,#0e1729);box-shadow:0 0 24px #d6ad5520}
.nx-name{font-size:21px;font-weight:800;letter-spacing:.18em;color:#f2f5ff}.nx-sub{font:10px 'DM Mono';letter-spacing:.14em;color:#d6ad55;margin-top:3px}
.eyebrow{font:11px 'DM Mono';letter-spacing:.17em;color:#d6ad55;text-transform:uppercase;margin-bottom:7px}
.hero{padding:25px 28px;border:1px solid #344b70;border-radius:20px;background:linear-gradient(115deg,#172b4cdd,#101a2bdd 60%,#18253a);position:relative;overflow:hidden;margin-bottom:20px}
.hero:after{content:'';position:absolute;right:-70px;top:-120px;width:340px;height:340px;border:1px solid #d6ad5540;border-radius:50%;box-shadow:0 0 0 25px #d6ad5508,0 0 0 55px #d6ad5505}
.hero h1{font-size:32px;margin:0 0 8px}.hero p{max-width:760px;color:#b7c7df;margin:0}
.panel{background:linear-gradient(145deg,#13213a,#0e1829);border:1px solid #2a4164;border-radius:16px;padding:18px 20px;margin-bottom:14px}
.panel-title{font-weight:800;color:#eef3ff;font-size:15px;margin-bottom:10px}
.mono{font:11px 'DM Mono';color:#a5b6d2;letter-spacing:.05em}
.chip{display:inline-block;padding:5px 9px;border:1px solid #425b83;border-radius:99px;color:#d8e3f5;font-size:11px;margin:2px;background:#162744}
.gold{color:#e1bc69}.muted{color:#91a2bd}.venue{border:1px solid #49648c;background:linear-gradient(145deg,#1a3155,#12213a);border-radius:12px;padding:12px;min-height:92px}
.venue b{color:#f4f6ff}.venue small{color:#a9bddc}.venue-dot{color:#e0b95f;font-size:11px}
.floor{border:1px solid #40577a;background:#0c1728;border-radius:18px;padding:18px;background-image:linear-gradient(#ffffff08 1px,transparent 1px),linear-gradient(90deg,#ffffff08 1px,transparent 1px);background-size:24px 24px}
.stTabs [data-baseweb="tab-list"]{gap:8px}.stTabs [data-baseweb="tab"]{background:#101c30;border:1px solid #2b4164;border-radius:9px;color:#c7d3e7;padding:9px 15px}.stTabs [aria-selected="true"]{background:#203b70!important;border-color:#d6ad55!important;color:white!important}
small{color:#91a2bd}
</style>''',unsafe_allow_html=True)

# ---------- Database ----------
def db():
    c=sqlite3.connect(DB_PATH,check_same_thread=False); c.row_factory=sqlite3.Row; return c

def init_db():
    c=db(); q=c.cursor()
    q.executescript('''
    CREATE TABLE IF NOT EXISTS venues(id INTEGER PRIMARY KEY,name TEXT UNIQUE,building TEXT,capacity INTEGER,kind TEXT,facilities TEXT,accessibility TEXT,status TEXT DEFAULT 'Active');
    CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY,title TEXT,department TEXT,club TEXT,category TEXT,organiser TEXT,description TEXT,expected INTEGER,venue_id INTEGER,start_at TEXT,end_at TEXT,budget REAL,fee REAL,registration_state TEXT,approval_state TEXT,event_state TEXT,created_at TEXT);
    CREATE TABLE IF NOT EXISTS approvals(id INTEGER PRIMARY KEY,event_id INTEGER,role TEXT,approver TEXT,decision TEXT DEFAULT 'Pending',comments TEXT,decided_at TEXT);
    CREATE TABLE IF NOT EXISTS registrations(id INTEGER PRIMARY KEY,event_id INTEGER,participant_id TEXT UNIQUE,name TEXT,email TEXT,phone TEXT,payment_amount REAL,reference TEXT,payment_status TEXT,registration_status TEXT,created_at TEXT);
    CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY,event_id INTEGER,title TEXT,assignee TEXT,team TEXT,due_date TEXT,status TEXT,priority TEXT,notes TEXT);
    CREATE TABLE IF NOT EXISTS blocks(id INTEGER PRIMARY KEY,title TEXT,start_at TEXT,end_at TEXT,block_type TEXT,notes TEXT);
    CREATE TABLE IF NOT EXISTS budgets(id INTEGER PRIMARY KEY,event_id INTEGER,category TEXT,planned REAL,actual REAL,payee TEXT,payment_status TEXT,notes TEXT);
    CREATE TABLE IF NOT EXISTS sponsors(id INTEGER PRIMARY KEY,event_id INTEGER,name TEXT,tier TEXT,promised REAL,received REAL,status TEXT,notes TEXT);
    CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY,action TEXT,entity TEXT,details TEXT,created_at TEXT);
    ''')
    if q.execute('SELECT COUNT(*) FROM venues').fetchone()[0]==0:
        venues=[('Main Auditorium','Academic Block A',650,'Indoor','Stage, Projector, 4 Microphones, Speakers, AC, Wi-Fi','Ramp access, ground-level entry'),('Seminar Hall 1','Academic Block B',180,'Indoor','Projector, 2 Microphones, Speakers, AC','Lift access'),('Seminar Hall 2','Academic Block B',120,'Indoor','Projector, Microphone, AC, Wi-Fi','Lift access'),('Open Air Theatre','Central Courtyard',500,'Outdoor','Stage, Speakers, Power','Step-free side access'),('Innovation Lab','Innovation Centre',70,'Indoor','Projector, Workstations, Wi-Fi, Power','Lift access'),('Quadrangle','Central Courtyard',300,'Outdoor','Power, Open seating','Ground-level access')]
        q.executemany('INSERT INTO venues(name,building,capacity,kind,facilities,accessibility) VALUES(?,?,?,?,?,?)',venues)
    if q.execute('SELECT COUNT(*) FROM events').fetchone()[0]==0:
        today=date.today(); evs=[('NEXUS Tech Summit','CSE','CSI Student Chapter','Conference','Aarav Mehta','Annual technology summit',420,1,(today+timedelta(days=12)).isoformat()+' 09:00',(today+timedelta(days=12)).isoformat()+' 17:00',85000,150,'Open','Approved','Scheduled'),('Design Sprint 2026','Design','Design Club','Workshop','Mira Rao','Product design sprint',95,2,(today+timedelta(days=18)).isoformat()+' 10:00',(today+timedelta(days=18)).isoformat()+' 16:00',22000,50,'Open','Under Review','Proposed'),('DataVerse Hack Night','Data Science','DS Forum','Hackathon','Ishaan Nair','Overnight data challenge',160,4,(today+timedelta(days=25)).isoformat()+' 16:00',(today+timedelta(days=26)).isoformat()+' 08:00',60000,100,'Draft','Changes Requested','Proposed')]
        for e in evs:
            q.execute('INSERT INTO events(title,department,club,category,organiser,description,expected,venue_id,start_at,end_at,budget,fee,registration_state,approval_state,event_state,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(*e,datetime.now().isoformat()))
        e1=q.execute('SELECT id FROM events WHERE title=?',('NEXUS Tech Summit',)).fetchone()[0]
        q.executemany('INSERT INTO approvals(event_id,role,approver,decision,comments,decided_at) VALUES(?,?,?,?,?,?)',[(e1,'Faculty Coordinator','Dr. Kavya Rao','Approved','Department endorsed.',datetime.now().isoformat()),(e1,'HOD','Dr. Ramesh Bhat','Approved','Venue and schedule reviewed.',datetime.now().isoformat()),(e1,'Principal','Dr. Ananya Iyer','Pending','Awaiting final sign-off.',None)])
        e2=q.execute('SELECT id FROM events WHERE title=?',('Design Sprint 2026',)).fetchone()[0]
        q.executemany('INSERT INTO approvals(event_id,role,approver,decision) VALUES(?,?,?,?)',[(e2,'Faculty Coordinator','Prof. Neha S','Pending'),(e2,'HOD','Dr. Ramesh Bhat','Pending'),(e2,'Principal','Dr. Ananya Iyer','Pending')])
        q.executemany('INSERT INTO registrations(event_id,participant_id,name,email,phone,payment_amount,reference,payment_status,registration_status,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)',[(e1,'NX-26-A81K','Ananya S','ananya.demo@example.com','9000000001',150,'DEMOUPI001','Verified','Confirmed',datetime.now().isoformat()),(e1,'NX-26-B92L','Rahul K','rahul.demo@example.com','9000000002',150,'DEMOUPI002','Pending Verification','Verification Pending',datetime.now().isoformat()),(e1,'NX-26-C73M','Nisha P','nisha.demo@example.com','9000000003',0,'','Unpaid','Payment Pending',datetime.now().isoformat()),(e1,'NX-26-D64N','Dev M','dev.demo@example.com','9000000004',150,'DEMOUPI001','Duplicate Reference','Verification Pending',datetime.now().isoformat())])
        q.executemany('INSERT INTO tasks(event_id,title,assignee,team,due_date,status,priority,notes) VALUES(?,?,?,?,?,?,?,?)',[(e1,'Confirm keynote speaker','Mira Rao','Speakers',(today+timedelta(days=4)).isoformat(),'In Progress','High','Follow up on final confirmation.'),(e1,'Publish event creatives','Rohan S','Marketing',(today+timedelta(days=3)).isoformat(),'Done','Medium','Social media creative approved.'),(e1,'Arrange AV equipment','Kiran P','Logistics',(today+timedelta(days=7)).isoformat(),'To Do','High','Check microphone and projector availability.')])
        q.executemany('INSERT INTO budgets(event_id,category,planned,actual,payee,payment_status,notes) VALUES(?,?,?,?,?,?,?)',[(e1,'Venue & logistics',18000,12000,'Campus Facilities','Paid','Advance recorded'),(e1,'Food & hospitality',25000,8000,'Campus Caterers','Partially Paid','Balance pending'),(e1,'Marketing & printing',9000,4500,'Print Studio','Paid',''),(e1,'Prizes',20000,0,'TBD','Unpaid','Quotes awaited')])
        q.executemany('INSERT INTO sponsors(event_id,name,tier,promised,received,status,notes) VALUES(?,?,?,?,?,?,?)',[(e1,'Aster Labs','Gold',50000,30000,'Partially Received','Demo sponsor'),(e1,'ByteBridge','Community',15000,15000,'Received','')])
    c.commit(); c.close()

init_db()

def rows(sql,args=()):
    c=db(); out=[dict(x) for x in c.execute(sql,args).fetchall()]; c.close(); return out

def run(sql,args=()):
    c=db(); cur=c.execute(sql,args); c.commit(); rid=cur.lastrowid; c.close(); return rid

def log(action,entity,details): run('INSERT INTO audit(action,entity,details,created_at) VALUES(?,?,?,?)',(action,entity,details,datetime.now().isoformat(timespec='seconds')))

def money(x): return '₹{:,.0f}'.format(float(x or 0))
def badge(text):
    colors={'Approved':'#244c3d','Pending':'#4c3c1d','Under Review':'#263f70','Rejected':'#542d38','Verified':'#244c3d','Unpaid':'#4c3c1d','Done':'#244c3d','In Progress':'#263f70','To Do':'#30384b','Changes Requested':'#542d38'}
    return f'<span class="chip" style="background:{colors.get(text,"#24334d")};border-color:#526a91">{text}</span>'

def header(kicker,title,sub=''):
    st.markdown(f'<div class="eyebrow">{kicker}</div><h1 style="margin:0 0 5px">{title}</h1><p class="muted" style="margin-top:0">{sub}</p>',unsafe_allow_html=True)

def event_options():
    ev=rows('SELECT id,title FROM events ORDER BY start_at'); return {x['title']:x['id'] for x in ev}

# ---------- Venue availability calendar (used when creating an event) ----------
DAY_START_MIN,DAY_END_MIN=9*60,17*60   # campus working day: a date is "full" when bookings cover 09:00-17:00
def _fmt_min(m): return f'{m//60:02d}:{m%60:02d}'
def venue_day_usage(venue_id):
    """{iso_date: [(start_min,end_min,label,is_block)]} for one venue (+ campus-wide date blocks)."""
    usage={}
    evs=rows("SELECT title,start_at,end_at FROM events WHERE venue_id=? AND event_state NOT IN ('Cancelled','Archived')",(venue_id,))
    bks=rows('SELECT title,start_at,end_at FROM blocks')
    for items,is_block in ((evs,False),(bks,True)):
        for x in items:
            try:
                s=datetime.strptime(str(x['start_at'])[:16],'%Y-%m-%d %H:%M'); e=datetime.strptime(str(x['end_at'])[:16],'%Y-%m-%d %H:%M')
            except Exception: continue
            if e<=s: continue
            d=s.date()
            while d<=e.date():
                ds=s.hour*60+s.minute if d==s.date() else 0
                de=e.hour*60+e.minute if d==e.date() else 1440
                if de>ds: usage.setdefault(d.isoformat(),[]).append((ds,de,x['title'],is_block))
                d+=timedelta(days=1)
    return usage
def _day_is_full(slots):
    cur=DAY_START_MIN
    for s,e,_,_ in sorted(slots):
        if s>cur: break
        cur=max(cur,e)
    return cur>=DAY_END_MIN
def availability_html(usage,year,month):
    today=date.today()
    css='''<style>.avcal{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:6px;margin:8px 0 6px}.avh{font:11px 'DM Mono';letter-spacing:.1em;color:#d6ad55;text-align:center;padding:4px 0}.avd{min-height:84px;border:1px solid #2b4164;border-radius:10px;padding:6px 7px;background:#0c1728;display:flex;flex-direction:column;gap:2px;overflow:hidden}.avd.empty{border:none;background:transparent}.avd.past{opacity:.45}.avd.today{border-color:#d6ad55}.avd .n{font-weight:800;color:#edf3ff;font-size:14px}.avd .t{font:10.5px 'DM Mono';color:#e1bc69;line-height:1.25}.avd .tl{font:700 10px 'DM Mono';color:#f0a3b3;letter-spacing:.06em;text-transform:uppercase}.avd.part{background:#14223a;border-color:#4a6490}.avd.full{background:repeating-linear-gradient(135deg,#2a1c28,#2a1c28 7px,#38222f 7px,#38222f 14px);border-color:#b56b7c}.avd.full .n s{color:#f0a3b3;text-decoration-thickness:2px}.avleg{display:flex;gap:14px;flex-wrap:wrap;font-size:12px;color:#91a2bd;margin-bottom:4px}.avleg i{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:5px;vertical-align:-2px}@media(max-width:700px){.avd{min-height:64px;padding:4px}.avd .t{font-size:9px}}</style>'''
    parts=[css,'<div class="avcal">']+[f'<div class="avh">{d}</div>' for d in ['MON','TUE','WED','THU','FRI','SAT','SUN']]
    for week in _calendar.Calendar(firstweekday=0).monthdayscalendar(year,month):
        for dn in week:
            if dn==0: parts.append('<div class="avd empty"></div>'); continue
            d=date(year,month,dn); slots=usage.get(d.isoformat(),[]); full=_day_is_full(slots)
            cls='avd'+(' full' if full else (' part' if slots else ''))+(' past' if d<today else '')+(' today' if d==today else '')
            lines=('<span class="tl">Full day</span>' if full else '')
            ordered=sorted(slots)
            for s,e,lab,isb in ordered[:3]:
                lines+=f'<span class="t">{_fmt_min(s)}–{_fmt_min(e)}{" · blocked" if isb else ""}</span>'
            if len(ordered)>3: lines+=f'<span class="t">+{len(ordered)-3} more</span>'
            tip=_html.escape('; '.join(f'{lab} ({_fmt_min(s)}–{_fmt_min(e)})' for s,e,lab,_ in ordered),quote=True)
            parts.append(f'<div class="{cls}" title="{tip}"><span class="n">{"<s>"+str(dn)+"</s>" if full else dn}</span>{lines}</div>')
    parts.append('</div><div class="avleg"><span><i style="background:#0c1728;border:1px solid #2b4164"></i>Free all day</span><span><i style="background:#14223a;border:1px solid #4a6490"></i>Part booked (times shown)</span><span><i style="background:#38222f;border:1px solid #b56b7c"></i>Full day taken (struck through)</span></div>')
    return ''.join(parts)


# Public participant registration route: /?register=<slug>&event_id=<id>
public_event_id=st.query_params.get('event_id')
public_slug=st.query_params.get('register')
if public_event_id and public_slug:
    public_event=rows('SELECT * FROM events WHERE id=?',(public_event_id,))
    st.markdown('<div class="nx-brand"><div class="nx-mark">✦</div><div><div class="nx-name">NEXORA</div><div class="nx-sub">CAMPUS REGISTRATION PORTAL</div></div></div>',unsafe_allow_html=True)
    if not public_event:
        st.error('This event registration link is invalid.')
    else:
        public_event=public_event[0]
        st.markdown(f'<div class="hero"><div class="eyebrow">PARTICIPANT REGISTRATION</div><h1>{public_event["title"]}</h1><p>{public_event["description"] or "Register to participate in this campus event."}</p><div style="margin-top:14px"><span class="chip">{public_event["department"]}</span><span class="chip">Fee: {money(public_event["fee"])}</span><span class="chip">Expected capacity: {public_event["expected"]}</span></div></div>',unsafe_allow_html=True)
        if public_event['registration_state']!='Open':
            st.warning('Registration is currently closed or paused for this event.')
        else:
            with st.form('public_registration'):
                full_name=st.text_input('Full name*'); email=st.text_input('Email address*'); phone=st.text_input('Phone number'); pay_ref=st.text_input('Payment reference (leave blank if not paid)'); submitted_amount=st.number_input('Amount paid (₹)',min_value=0.0,value=float(public_event['fee']),step=50.0)
                consent=st.checkbox('I confirm that the information provided is accurate.')
                submit_public=st.form_submit_button('Submit registration',use_container_width=True)
            if submit_public:
                if not full_name.strip() or not email.strip(): st.error('Name and email are required.')
                elif not consent: st.error('Please confirm your details before submitting.')
                elif rows('SELECT id FROM registrations WHERE event_id=? AND lower(email)=lower(?)',(public_event['id'],email)): st.error('This email is already registered for this event.')
                else:
                    new_pid='NX-'+date.today().strftime('%y')+'-'+''.join(secrets.choice(string.ascii_uppercase+string.digits) for _ in range(6))
                    duplicate=bool(pay_ref.strip()) and bool(rows('SELECT id FROM registrations WHERE lower(reference)=lower(?)',(pay_ref.strip(),)))
                    if duplicate: pay_state='Duplicate Reference'
                    elif submitted_amount<=0: pay_state='Unpaid'
                    elif not pay_ref.strip(): pay_state='Missing Reference'
                    elif submitted_amount<float(public_event['fee']): pay_state='Partially Paid'
                    else: pay_state='Pending Verification'
                    reg_state='Payment Pending' if pay_state in ['Unpaid','Missing Reference','Partially Paid'] else 'Verification Pending'
                    run('INSERT INTO registrations(event_id,participant_id,name,email,phone,payment_amount,reference,payment_status,registration_status,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)',(public_event['id'],new_pid,full_name,email,phone,submitted_amount,pay_ref,pay_state,reg_state,datetime.now().isoformat()))
                    log('Public registration','Registration',new_pid+' / '+full_name)
                    st.success('Registration submitted. Save your participant ID: '+new_pid)
                    st.info('Your registration is pending payment verification by the event finance team. This form does not process or verify a bank/UPI payment.')
    st.stop()

# ---------- Access control: landing page + role sign-in ----------
ROLE_INFO={
    'Student':  {'icon':'🎓','blurb':'Propose events, manage registrations and run committee tasks.'},
    'Faculty':  {'icon':'📖','blurb':'Review proposals as Faculty Coordinator and guide committees.'},
    'HOD':      {'icon':'🏛️','blurb':'Give departmental approval and oversee events and reports.'},
    'Principal':{'icon':'⚜️','blurb':'Final sign-off, institution-wide oversight and audit.'},
}
# Workspaces each profile can see (nothing else is shown to that profile)
NAV={
    'Student':  ['Command Center','Events & Approvals','Campus Blueprint','Calendar & Slots','Registrations & Payments','Committee Tasks'],
    'Faculty':  ['Command Center','Events & Approvals','Campus Blueprint','Calendar & Slots','Registrations & Payments','Committee Tasks','Finance & Sponsors'],
    'HOD':      ['Command Center','Events & Approvals','Campus Blueprint','Calendar & Slots','Registrations & Payments','Committee Tasks','Finance & Sponsors','Analytics & Reports'],
    'Principal':['Command Center','Events & Approvals','Campus Blueprint','Calendar & Slots','Committee Tasks','Finance & Sponsors','Analytics & Reports','Admin & Audit'],
}
# Which step of the approval chain each profile may decide
STEP={'Faculty':'Faculty Coordinator','HOD':'HOD','Principal':'Principal'}

# Demo passwords are stored as salted SHA-256 hashes (see README). Override any of them with an
# environment variable, e.g.  NEXORA_PW_HOD=my-new-password
_DEFAULT_PW_HASH={
    'Student':'b219714ce83db99fda0ab69196fb2b2b00726af2100a6c40fddce08d53e6e1d4',
    'Faculty':'979fe19e6684f501f1f953d4e6e66f769f97b2a4d9d6f1475c608dd5d0e37775',
    'HOD':'a7988f0469cbd34567c97c83d5fe5ea8bc9b4d3903dfb13817abd99bcf624749',
    'Principal':'c3eb3f6645a93157eb0b8518402690d44bc27557e25311824419a4a2ccec8dd5',
}
def _load_env_file():
    # Reads KEY=VALUE lines from a ".env" file next to app.py (no extra package needed).
    f=APP_DIR/'.env'
    if not f.exists(): return
    for line in f.read_text(encoding='utf-8').splitlines():
        line=line.strip()
        if not line or line.startswith('#') or '=' not in line: continue
        k,v=line.split('=',1); v=v.strip().strip('"').strip("'")
        if k.strip() and v: os.environ.setdefault(k.strip(),v)
_load_env_file()
def _pw_hash(p): return hashlib.sha256(('nexora-v1::'+p).encode('utf-8')).hexdigest()
def _check_password(r,p):
    env=os.environ.get('NEXORA_PW_'+r.upper())
    expected=_pw_hash(env) if env else _DEFAULT_PW_HASH[r]
    return hmac.compare_digest(_pw_hash(p),expected)

def make_tabs(names):
    return dict(zip(names,st.tabs(names)))

if not st.session_state.get('auth_role'):
    st.markdown('''<style>
    section[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"],[data-testid="collapsedControl"]{display:none!important}
    .block-container{max-width:1180px}
    .lp-top{display:flex;align-items:center;gap:12px;padding:6px 2px 0}
    .lp-hero{text-align:center;padding:46px 20px 30px}
    .lp-title{font-size:clamp(34px,5.6vw,62px);font-weight:800;letter-spacing:-.04em;line-height:1.05;margin:6px 0 16px;color:#f2f5ff}
    .lp-sub{max-width:760px;margin:0 auto;font-size:17px;line-height:1.65;color:#b7c7df}
    .lp-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:26px 0 34px}
    .lp-card{border:1px solid #2f4770;border-radius:16px;padding:18px 20px;background:linear-gradient(145deg,#13213a,#0e1829)}
    .lp-card b{display:block;color:#e3bd69;letter-spacing:.14em;font:600 12px 'DM Mono';text-transform:uppercase;margin-bottom:8px}
    .lp-card span{color:#b7c7df;font-size:14px;line-height:1.55}
    .lp-signin{border:1px solid #344b70;border-radius:20px;padding:24px 26px 8px;background:linear-gradient(115deg,#172b4cdd,#101a2bdd 60%,#18253a);margin-bottom:10px}
    .lp-step{font:11px 'DM Mono';letter-spacing:.17em;color:#d6ad55;text-transform:uppercase;margin:0 0 4px}
    .lp-q{font-size:22px;font-weight:800;color:#f2f5ff;margin:0 0 12px;letter-spacing:-.02em}
    .lp-desc{font-size:12.5px;color:#91a2bd;line-height:1.45;min-height:54px;margin:-4px 2px 10px}
    [data-testid="stBaseButton-primary"],[data-testid="stBaseButton-primaryFormSubmit"]{background:linear-gradient(135deg,#d6ad55,#b98d34)!important;border:1px solid #e8c878!important;color:#10182a!important;font-weight:800!important}
    [data-testid="stBaseButton-secondaryFormSubmit"]{border-radius:10px;border:1px solid #4967a0;background:linear-gradient(135deg,#3158c9,#24449f);color:white;font-weight:700}
    @media(max-width:760px){.lp-grid{grid-template-columns:1fr}}
    </style>''',unsafe_allow_html=True)
    st.markdown('<div class="lp-top"><div class="nx-mark">✦</div><div><div class="nx-name">NEXORA</div><div class="nx-sub">CAMPUS COORDINATION OS</div></div></div>',unsafe_allow_html=True)
    st.markdown('''<div class="lp-hero"><div class="eyebrow">One platform · Every stakeholder</div>
    <h1 class="lp-title">Connect. Coordinate. <span class="gold">Optimise.</span></h1>
    <p class="lp-sub">NEXORA brings students, faculty, HODs and the Principal onto one workspace, so every campus event moves from idea to approval to execution without the chasing, clashes and paperwork.</p></div>
    <div class="lp-grid">
    <div class="lp-card"><b>◈ Connect</b><span>Every stakeholder works from one shared, always-current view of events, venues and decisions.</span></div>
    <div class="lp-card"><b>◈ Coordinate</b><span>Approvals, registrations and committee tasks move in a clear sequence, with each decision recorded.</span></div>
    <div class="lp-card"><b>◈ Optimise</b><span>Clash-free scheduling, transparent finance and live analytics help the campus achieve more with less effort.</span></div>
    </div>''',unsafe_allow_html=True)

    _,mid,_=st.columns([0.35,4,0.35])
    with mid:
        st.markdown('<div class="lp-signin"><div class="lp-step">Step 1 of 2</div><div class="lp-q">Who is signing in?</div></div>',unsafe_allow_html=True)
        picked=st.session_state.get('pick')
        cols=st.columns(4)
        for col,(r,info) in zip(cols,ROLE_INFO.items()):
            with col:
                st.button(f"{info['icon']}  {r}",key=f'pick_{r}',use_container_width=True,type='primary' if picked==r else 'secondary',on_click=lambda r=r: st.session_state.update(pick=r))
                st.markdown(f'<div class="lp-desc">{info["blurb"]}</div>',unsafe_allow_html=True)
        if not picked:
            st.caption('Select your role to continue.')
        else:
            st.markdown(f'<div class="lp-step" style="margin-top:6px">Step 2 of 2</div><div class="lp-q" style="font-size:19px">Enter the {picked} password</div>',unsafe_allow_html=True)
            locked=st.session_state.get('lock_until',0)-time.time()
            with st.form('login_form'):
                pw=st.text_input('Password',type='password',placeholder=f'{picked} password',label_visibility='collapsed')
                go=st.form_submit_button(f'Sign in as {picked}',type='primary',use_container_width=True)
            if go:
                if locked>0:
                    st.error(f'Too many unsuccessful attempts. Please wait {int(locked)+1} seconds and try again.')
                elif _check_password(picked,pw or ''):
                    st.session_state.update(auth_role=picked,fails=0); st.session_state.pop('lock_until',None)
                    log('Sign in','Session',picked); st.rerun()
                else:
                    fails=st.session_state.get('fails',0)+1; st.session_state['fails']=fails
                    log('Failed sign-in','Session',picked)
                    if fails>=5: st.session_state.update(lock_until=time.time()+30,fails=0); st.error('Too many unsuccessful attempts. Sign-in is paused for 30 seconds.')
                    else: st.error('Incorrect password for this role. Please try again.')
            st.caption('Access is limited to your role. Contact your administrator if you have forgotten your password.')
    st.markdown('---')
    st.markdown('<div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap"><span class="mono">NEXORA · CONNECT. COORDINATE. OPTIMISE.</span><span class="mono">PROTOTYPE BUILD · DEMO ACCESS CONTROL</span></div>',unsafe_allow_html=True)
    st.stop()


# ---------- Sidebar ----------
role=st.session_state['auth_role']
with st.sidebar:
    st.markdown('<div class="nx-brand"><div class="nx-mark">✦</div><div><div class="nx-name">NEXORA</div><div class="nx-sub">CAMPUS COORDINATION OS</div></div></div>',unsafe_allow_html=True)
    page=st.radio('WORKSPACE',NAV[role],label_visibility='collapsed')
    st.markdown('---')
    st.markdown(f'<div class="mono">SIGNED IN AS</div><div style="margin:6px 0 10px"><span class="chip" style="border-color:#d6ad55">{ROLE_INFO[role]["icon"]} {role}</span></div>',unsafe_allow_html=True)
    if st.button('Sign out',use_container_width=True):
        log('Sign out','Session',role); st.session_state.clear(); st.rerun()
    st.markdown('<div class="mono" style="margin-top:14px">DEMO ENVIRONMENT · LOCAL SQLITE</div>',unsafe_allow_html=True)
    st.caption('Prototype mode · use synthetic participant and payment data only.')

# ---------- Command Center ----------
if page=='Command Center':
    ev=rows('SELECT * FROM events'); regs=rows('SELECT * FROM registrations'); apps=rows("SELECT * FROM approvals WHERE decision='Pending'"); tasks=rows("SELECT * FROM tasks WHERE status!='Done'")
    st.markdown(f'''<div class="hero"><div class="eyebrow">CAMPUS INTELLIGENCE / {date.today().strftime('%d %b %Y').upper()} · {role.upper()} VIEW</div><h1>One campus. Every moving part.</h1><p>NEXORA brings event planning, approvals, venues, registrations, finance and committee execution into one coordinated operating layer.</p><div style="margin-top:16px"><span class="chip">✦ Live local workspace</span><span class="chip">Constraint-based scheduling</span><span class="chip">Auditable workflows</span></div></div>''',unsafe_allow_html=True)
    all_apps=rows('SELECT * FROM approvals'); step=STEP.get(role)
    mine=[a for a in all_apps if a['decision']=='Pending' and a['role']==step and all(x['decision']=='Approved' for x in all_apps if x['event_id']==a['event_id'] and x['id']<a['id'])]
    to_review=sum(x['payment_status'] in ['Pending Verification','Duplicate Reference'] for x in regs); open_regs=sum(x['registration_state']=='Open' for x in ev)
    if role=='Student':
        metrics=[('Total events',len(ev)),('Open for registration',open_regs),('Registrations',len(regs)),('Open tasks',len(tasks))]
        attention=[(f'{open_regs} events open for registration','Registrations'),(f'{len(tasks)} committee tasks remain open','Execution desk')]
    elif role=='Principal':
        metrics=[('Total events',len(ev)),('Awaiting my sign-off',len(mine)),('Open tasks',len(tasks)),('Venues',len(rows('SELECT id FROM venues')))]
        attention=[(f'{len(mine)} proposals await your sign-off','Approval desk'),(f'{len(tasks)} committee tasks remain open','Execution desk')]
    else:
        metrics=[('Total events',len(ev)),('Awaiting my approval',len(mine)),('Registrations',len(regs)),('Payments to review',to_review),('Open tasks',len(tasks))]
        attention=[(f'{len(mine)} approvals need your decision','Approval desk'),(f'{to_review} payments need review','Finance desk'),(f'{len(tasks)} committee tasks remain open','Execution desk')]
    for col,(lbl,val) in zip(st.columns(len(metrics)),metrics): col.metric(lbl,val)
    st.markdown('### Operational overview')
    left,right=st.columns([1.35,1])
    with left:
        st.markdown('<div class="panel"><div class="panel-title">Upcoming event pipeline</div>',unsafe_allow_html=True)
        if ev:
            df=pd.DataFrame(ev); df['start_at']=pd.to_datetime(df['start_at']); df=df.sort_values('start_at')
            for _,x in df.head(5).iterrows():
                st.markdown(f'''<div style="display:flex;justify-content:space-between;gap:12px;padding:12px 0;border-bottom:1px solid #263b5b"><div><b>{x['title']}</b><div class="mono">{x['department']} · {x['start_at'].strftime('%d %b, %H:%M')}</div></div><div>{badge(x['approval_state'])}</div></div>''',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel"><div class="panel-title">Attention queue</div>',unsafe_allow_html=True)
        for a,b in attention: st.markdown(f'<div style="padding:13px 0;border-bottom:1px solid #263b5b"><div class="gold" style="font-weight:800">{a}</div><div class="mono">{b}</div></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    st.markdown('### Campus at a glance')
    v=rows('SELECT * FROM venues'); cols=st.columns(3)
    for i,x in enumerate(v):
        with cols[i%3]: st.markdown(f'<div class="venue" style="margin-bottom:10px"><div class="venue-dot">◈ {x["building"]}</div><b>{x["name"]}</b><br><small>Capacity {x["capacity"]} · {x["kind"]}</small></div>',unsafe_allow_html=True)

# ---------- Events & Approvals ----------
elif page=='Events & Approvals':
    header('WORKFLOW / 01','Events & approvals','Create proposals, route decisions and track the event lifecycle from one workspace.')
    _tt=make_tabs(['Event portfolio']+(['Create event'] if role!='Principal' else [])+(['Approval desk'] if role!='Student' else [])); tab1=_tt['Event portfolio']; tab2=_tt.get('Create event'); tab3=_tt.get('Approval desk')
    with tab1:
        data=rows('SELECT e.*,v.name venue FROM events e LEFT JOIN venues v ON e.venue_id=v.id ORDER BY e.start_at')
        if data: st.dataframe(pd.DataFrame(data)[['title','department','club','venue','start_at','expected','approval_state','event_state','registration_state']],use_container_width=True,hide_index=True)
        else: st.info('No events yet. Create your first event.')
        if data:
            chosen=st.selectbox('Open event workspace',[x['title'] for x in data]); e=next(x for x in data if x['title']==chosen)
            a,b,c=st.columns(3); a.metric('Expected participants',e['expected']); b.metric('Budget',money(e['budget'])); c.metric('Registration fee',money(e['fee']))
            st.markdown(f"**Description:** {e['description']}  \n**Organiser:** {e['organiser']}  ·  **Venue:** {e['venue']}  ·  **Status:** {e['event_state']}")
            if role!='Principal':
                with st.form('event_edit'):
                    state=st.selectbox('Lifecycle status',['Proposed','Scheduled','Registration Open','Registration Closed','Completed','Financially Closed','Archived'],index=['Proposed','Scheduled','Registration Open','Registration Closed','Completed','Financially Closed','Archived'].index(e['event_state']) if e['event_state'] in ['Proposed','Scheduled','Registration Open','Registration Closed','Completed','Financially Closed','Archived'] else 0)
                    regstate=st.selectbox('Registration control',['Draft','Open','Paused','Closed'],index=['Draft','Open','Paused','Closed'].index(e['registration_state']) if e['registration_state'] in ['Draft','Open','Paused','Closed'] else 0)
                    if st.form_submit_button('Save event status'):
                        run('UPDATE events SET event_state=?,registration_state=? WHERE id=?',(state,regstate,e['id'])); log('Updated event','Event',f'{e["title"]}: {state}, registrations {regstate}'); st.success('Event workspace updated.'); st.rerun()
    if tab2 is not None:
        with tab2:
            venues=rows('SELECT * FROM venues ORDER BY name'); vmap={v['name']:v['id'] for v in venues}
            if vmap:
                with st.expander('📅 Check venue availability before you propose',expanded=True):
                    av1,av2=st.columns(2)
                    av_venue=av1.selectbox('Venue to check',list(vmap),key='avail_venue')
                    _t0=date.today(); _months=[((_t0.year*12+_t0.month-1+i)//12,(_t0.year*12+_t0.month-1+i)%12+1) for i in range(12)]
                    av_ym=av2.selectbox('Month',_months,format_func=lambda ym: _calendar.month_name[ym[1]]+' '+str(ym[0]),key='avail_month')
                    st.markdown(availability_html(venue_day_usage(vmap[av_venue]),av_ym[0],av_ym[1]),unsafe_allow_html=True)
                    st.caption('Struck-through dates are fully taken (bookings or campus date blocks cover 09:00–17:00). Part-booked dates list the times already in use. Pick a free date or a free time window in the form below.')
            with st.form('new_event',clear_on_submit=True):
                c1,c2=st.columns(2); title=c1.text_input('Event title*'); dept=c2.text_input('Department*',placeholder='Data Science')
                c1,c2=st.columns(2); club=c1.text_input('Club / organiser group'); organiser=c2.text_input('Primary organiser')
                desc=st.text_area('Event description'); c1,c2,c3=st.columns(3); cat=c1.selectbox('Category',['Conference','Workshop','Hackathon','Cultural','Sports','Seminar','Competition','Other']); expected=c2.number_input('Expected participants',min_value=1,value=100); fee=c3.number_input('Registration fee (₹)',min_value=0.0,value=0.0,step=50.0)
                c1,c2=st.columns(2); venue=c1.selectbox('Preferred venue',list(vmap)); budget=c2.number_input('Proposed budget (₹)',min_value=0.0,value=10000.0,step=1000.0)
                c1,c2=st.columns(2); d=c1.date_input('Event date',value=date.today()+timedelta(days=14)); start=c1.time_input('Start time',value=datetime.strptime('09:00','%H:%M').time()); end=c2.time_input('End time',value=datetime.strptime('17:00','%H:%M').time())
                submitted=st.form_submit_button('Create proposal',use_container_width=True)
                if submitted:
                    if not title.strip() or not dept.strip(): st.error('Event title and department are required.')
                    elif end<=start: st.error('End time must be after start time.')
                    else:
                        sid=vmap[venue]; startat=f'{d.isoformat()} {start.strftime("%H:%M")}'; endat=f'{d.isoformat()} {end.strftime("%H:%M")}'
                        conflict=rows("SELECT e.title FROM events e WHERE e.venue_id=? AND e.event_state NOT IN ('Cancelled','Archived') AND e.start_at<? AND e.end_at>?",(sid,endat,startat))
                        blocked=rows('SELECT title FROM blocks WHERE start_at<? AND end_at>?',(endat,startat))
                        if conflict: st.error('Venue conflict: '+', '.join(x['title'] for x in conflict)+'. Choose another venue or time.')
                        elif blocked: st.error('Calendar restriction: '+', '.join(x['title'] for x in blocked)+'. Choose another date or time.')
                        else:
                            eid=run('INSERT INTO events(title,department,club,category,organiser,description,expected,venue_id,start_at,end_at,budget,fee,registration_state,approval_state,event_state,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(title,dept,club,cat,organiser,desc,expected,sid,startat,endat,budget,fee,'Draft','Submitted','Proposed',datetime.now().isoformat()))
                            for rname,appr in [('Faculty Coordinator','Faculty Coordinator'),('HOD','HOD'),('Principal','Principal')]: run('INSERT INTO approvals(event_id,role,approver,decision) VALUES(?,?,?,?)',(eid,rname,appr,'Pending'))
                            log('Created event','Event',title); st.success('Proposal created and approval chain generated.'); st.rerun()
    if tab3 is not None:
        with tab3:
            pending=rows("SELECT a.*,e.title event_title FROM approvals a JOIN events e ON e.id=a.event_id ORDER BY CASE a.decision WHEN 'Pending' THEN 0 ELSE 1 END,a.id")
            if pending:
                for a in pending:
                    with st.container(border=True):
                        l,r=st.columns([3,1]); l.markdown(f"**{a['event_title']}**  \n{a['role']} · {a['approver']} · {badge(a['decision'])}",unsafe_allow_html=True)
                        if a['decision']=='Pending':
                            prior=rows('SELECT decision FROM approvals WHERE event_id=? AND id<? ORDER BY id',(a['event_id'],a['id']))
                            my_step=(a['role']==STEP.get(role)); can_act=my_step and all(x['decision']=='Approved' for x in prior)
                            with r:
                                if not my_step:
                                    st.caption(f"Awaiting {a['role']} decision.")
                                elif not can_act:
                                    st.caption('Waiting for the previous approver in the chain.')
                                else:
                                    decision=st.selectbox('Decision',['Approve','Request Changes','Reject'],key=f"d{a['id']}")
                                    comment=st.text_input('Comment',key=f"c{a['id']}")
                                    if st.button('Record decision',key=f"b{a['id']}"):
                                        new={'Approve':'Approved','Request Changes':'Changes Requested','Reject':'Rejected'}[decision]
                                        run('UPDATE approvals SET decision=?,comments=?,decided_at=? WHERE id=?',(new,comment,datetime.now().isoformat(timespec='seconds'),a['id']))
                                        allsteps=rows('SELECT decision FROM approvals WHERE event_id=?',(a['event_id'],)); state='Approved' if all(x['decision']=='Approved' for x in allsteps) else ('Rejected' if new=='Rejected' else 'Changes Requested' if new=='Changes Requested' else 'Under Review')
                                        run('UPDATE events SET approval_state=? WHERE id=?',(state,a['event_id'])); log('Approval decision','Event',f"{a['event_title']} / {a['role']}: {new}"); st.success('Decision recorded.'); st.rerun()
                        else: st.caption(f"{a['comments'] or 'No comment'} · {a['decided_at'] or 'No timestamp'}")
            else: st.info('No approval records yet.')

# ---------- Campus Blueprint ----------
elif page=='Campus Blueprint':
    header('SPATIAL INTELLIGENCE / 02','Campus venue blueprint','A miniature, schematic campus view. Venue cards connect to capacity, facilities and booking availability.')
    venues=rows('SELECT * FROM venues ORDER BY id'); bookings=rows("SELECT e.title,e.start_at,e.end_at,e.event_state,v.name venue FROM events e JOIN venues v ON v.id=e.venue_id WHERE e.event_state NOT IN ('Cancelled','Archived')")
    st.markdown('<div class="floor"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px"><div><div class="eyebrow">ILLUSTRATIVE CAMPUS PLAN</div><b style="font-size:18px">NEXORA · Spatial overview</b></div><span class="chip">Not to scale · editable venue master</span></div>',unsafe_allow_html=True)
    # schematic layout: central spine and building clusters
    c1,c2,c3=st.columns([1,1.2,1])
    layouts=[('ACADEMIC BLOCK A',[venues[0]]),('CENTRAL COURTYARD',[venues[3],venues[5]]),('ACADEMIC BLOCK B',[venues[1],venues[2]])]
    for col,(building,items) in zip([c1,c2,c3],layouts):
        with col:
            st.markdown(f'<div class="eyebrow" style="margin-top:10px">{building}</div>',unsafe_allow_html=True)
            for v in items:
                current=[b for b in bookings if b['venue']==v['name']]
                status='Booked' if current else 'Available'
                st.markdown(f'<div class="venue" style="margin:9px 0"><div class="venue-dot">◈ {status.upper()}</div><b>{v["name"]}</b><br><small>{v["capacity"]} capacity · {v["kind"]}</small><br><small>{v["facilities"]}</small></div>',unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;padding:18px;border:1px dashed #425b83;border-radius:12px;margin-top:12px;color:#d6ad55">CAMPUS SPINE · Main walkway / access corridor</div><div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:9px;margin-top:14px"><div class="venue"><div class="venue-dot">CAMPUS SUPPORT</div><b>Admin Block</b><br><small>Administration · approvals</small></div><div class="venue"><div class="venue-dot">LEARNING ZONE</div><b>Library</b><br><small>Study · reading · resources</small></div><div class="venue"><div class="venue-dot">STUDENT LIFE</div><b>Canteen / Commons</b><br><small>Dining · informal gathering</small></div><div class="venue"><div class="venue-dot">RECREATION</div><b>Sports Zone</b><br><small>Grounds · outdoor activities</small></div></div><div style="display:flex;justify-content:space-around;margin-top:18px;gap:12px;flex-wrap:wrap"><span class="chip">◈ Main entry (schematic)</span><span class="chip">◈ Student commons</span><span class="chip">◈ Innovation Centre</span><span class="chip">◈ Parking / service access</span></div></div>',unsafe_allow_html=True)
    st.markdown('### Venue directory')
    for v in venues:
        with st.expander(f"{v['name']} · {v['building']} · capacity {v['capacity']}"):
            a,b=st.columns(2); a.write(f"**Type:** {v['kind']}  \n**Facilities:** {v['facilities']}"); b.write(f"**Accessibility:** {v['accessibility']}  \n**Status:** {v['status']}")
    if role in ('HOD','Principal'):
        st.markdown('### Maintain venue master')
        with st.form('add_venue'):
            a,b,c=st.columns(3); vn=a.text_input('Venue name'); building=b.text_input('Building / zone'); cap=c.number_input('Capacity',min_value=1,value=100)
            a,b=st.columns(2); kind=a.selectbox('Type',['Indoor','Outdoor']); facilities=b.text_input('Facilities',placeholder='Projector, Wi-Fi, speakers')
            access=st.text_input('Accessibility notes'); ok=st.form_submit_button('Add venue')
            if ok:
                try: run('INSERT INTO venues(name,building,capacity,kind,facilities,accessibility) VALUES(?,?,?,?,?,?)',(vn,building,cap,kind,facilities,access)); log('Added venue','Venue',vn); st.success('Venue added.'); st.rerun()
                except sqlite3.IntegrityError: st.error('A venue with this name already exists.')

# ---------- Calendar & Slots ----------
elif page=='Calendar & Slots':
    header('SCHEDULING / 03','Calendar & slot intelligence','See the campus schedule, create restricted periods and compare feasible venue options.')
    _tt=make_tabs(['Calendar agenda']+(['Date blocks'] if role!='Student' else [])+['Find a venue slot']); t1=_tt['Calendar agenda']; t2=_tt.get('Date blocks'); t3=_tt['Find a venue slot']
    with t1:
        events=rows('SELECT e.*,v.name venue FROM events e LEFT JOIN venues v ON v.id=e.venue_id ORDER BY e.start_at'); blocks=rows('SELECT * FROM blocks ORDER BY start_at')
        for e in events:
            st.markdown(f'<div class="panel"><div style="display:flex;justify-content:space-between"><b>{e["title"]}</b>{badge(e["approval_state"])}</div><div class="mono">{e["start_at"]} → {e["end_at"]} · {e["venue"]} · {e["department"]}</div></div>',unsafe_allow_html=True)
        if blocks:
            st.markdown('**Restricted periods**')
            st.dataframe(pd.DataFrame(blocks),use_container_width=True,hide_index=True)
    if t2 is not None:
        with t2:
            with st.form('block_form'):
                title=st.text_input('Block title',placeholder='Semester examinations'); typ=st.selectbox('Block type',['Examination','Holiday','Maintenance','College-wide event','Other']); a,b=st.columns(2); d1=a.date_input('Start date',value=date.today()+timedelta(days=20)); d2=b.date_input('End date',value=date.today()+timedelta(days=20)); notes=st.text_input('Notes'); ok=st.form_submit_button('Add date block')
                if ok:
                    if d2<d1: st.error('End date cannot be before start date.')
                    else: run('INSERT INTO blocks(title,start_at,end_at,block_type,notes) VALUES(?,?,?,?,?)',(title,d1.isoformat()+' 00:00',d2.isoformat()+' 23:59',typ,notes)); log('Created date block','Calendar',title); st.success('Date block saved.'); st.rerun()
            for b in blocks:
                if st.button(f"Delete block · {b['title']}",key=f"delblock{b['id']}"): run('DELETE FROM blocks WHERE id=?',(b['id'],)); st.rerun()
    with t3:
        # independent slot search area
        st.markdown('### Slot finder')
        venues=rows('SELECT * FROM venues'); a,b,c=st.columns(3); chosen=a.selectbox('Venue to evaluate',[x['name'] for x in venues],key='slotvenue'); v=next(x for x in venues if x['name']==chosen); day=b.date_input('Target date',value=date.today()+timedelta(days=14),key='slotdate'); expected=c.number_input('Expected attendance',min_value=1,value=100,key='slotcap')
        if expected>v['capacity']: st.warning(f"Capacity mismatch: {v['name']} holds {v['capacity']}; expected attendance is {expected}.")
        starttime=st.time_input('Preferred start',value=datetime.strptime('09:00','%H:%M').time(),key='slstart'); endtime=st.time_input('Preferred end',value=datetime.strptime('12:00','%H:%M').time(),key='slend')
        if st.button('Check feasibility'):
            s=f'{day.isoformat()} {starttime.strftime("%H:%M")}'; e=f'{day.isoformat()} {endtime.strftime("%H:%M")}'; conflicts=rows("SELECT title FROM events WHERE venue_id=? AND event_state NOT IN ('Cancelled','Archived') AND start_at<? AND end_at>?",(v['id'],e,s)); blocked=rows('SELECT title FROM blocks WHERE start_at<? AND end_at>?',(e,s))
            if endtime<=starttime: st.error('End time must be after start time.')
            elif conflicts or blocked or expected>v['capacity']:
                st.error('This slot is not feasible.');
                if conflicts: st.write('Venue conflicts:',', '.join(x['title'] for x in conflicts))
                if blocked: st.write('Calendar restrictions:',', '.join(x['title'] for x in blocked))
            else: st.success('Slot passes current venue, capacity and date-block checks. Approval availability must still be confirmed by the approvers.')
        st.markdown('### Recommend an available venue')
        required=st.multiselect('Required facilities', ['Projector','Microphone','Speakers','Stage','AC','Wi-Fi','Power','Workstations'])
        if st.button('Rank feasible venues'):
            s=f'{day.isoformat()} {starttime.strftime("%H:%M")}'; e=f'{day.isoformat()} {endtime.strftime("%H:%M")}'; blocked=rows('SELECT title FROM blocks WHERE start_at<? AND end_at>?',(e,s)); ranked=[]
            if endtime<=starttime: st.error('End time must be after start time.')
            elif blocked: st.error('No recommendation: this date/time intersects a campus block: '+', '.join(x['title'] for x in blocked))
            else:
                for venue_item in venues:
                    conflict=rows("SELECT id FROM events WHERE venue_id=? AND event_state NOT IN ('Cancelled','Archived') AND start_at<? AND end_at>?",(venue_item['id'],e,s))
                    facilities=venue_item['facilities'].lower(); matched=[x for x in required if x.lower() in facilities]; missing=[x for x in required if x.lower() not in facilities]
                    if not conflict and venue_item['capacity']>=expected:
                        capacity_fit=1-(venue_item['capacity']-expected)/max(venue_item['capacity'],1)
                        score=round((capacity_fit*.45 + (len(matched)/len(required) if required else 1)*.55)*100)
                        ranked.append({'Venue':venue_item['name'],'Capacity':venue_item['capacity'],'Fit score':score,'Facilities matched':', '.join(matched) or 'No specific requirement','Notes':'All requested facilities matched' if not missing else 'Missing: '+', '.join(missing)})
                if ranked:
                    st.dataframe(pd.DataFrame(sorted(ranked,key=lambda x:x['Fit score'],reverse=True)),use_container_width=True,hide_index=True)
                    st.caption('Rule-based ranking: capacity fit (45%) + requested facility match (55%). It checks current venue bookings and campus date blocks; it does not account for live approver availability.')
                else: st.warning('No venue meets the selected capacity and availability constraints.')

# ---------- Registrations & Payments ----------
elif page=='Registrations & Payments':
    header('PARTICIPANT OPERATIONS / 04','Registrations & payments','Open registration, generate shareable links and unique participant IDs, then verify each submitted payment.')
    evmap=event_options(); _tt=make_tabs(['Participant register','Add registration']+(['Payment review'] if role!='Student' else [])); t1=_tt['Participant register']; t2=_tt['Add registration']; t3=_tt.get('Payment review')
    with t1:
        selected=st.selectbox('Event',list(evmap),key='reg_event'); data=rows('SELECT * FROM registrations WHERE event_id=? ORDER BY id DESC',(evmap[selected],))
        if data: st.dataframe(pd.DataFrame(data),use_container_width=True,hide_index=True)
        else: st.info('No registrations for this event yet.')
        st.markdown('**Shareable registration link**')
        slug=''.join(ch.lower() if ch.isalnum() else '-' for ch in selected).strip('-').replace('--','-')
        base_url=st.text_input('App base URL (replace with your deployed URL when hosted)','http://localhost:8501',key='public_base_url').rstrip('/')
        st.code(f'{base_url}/?register={slug}&event_id={evmap[selected]}',language='text')
        st.caption('This link opens the public participant registration form. On another device, replace localhost with the app host URL reachable by that device.')
        csv=pd.DataFrame(data).to_csv(index=False).encode('utf-8')
        st.download_button('Export participant CSV',csv,file_name=f'{slug}_registrations.csv',mime='text/csv')
    with t2:
        selected=st.selectbox('Registration event',list(evmap),key='addreg_event'); event=rows('SELECT * FROM events WHERE id=?',(evmap[selected],))[0]
        if event['registration_state']!='Open': st.warning(f"Registration state is {event['registration_state']}. Set it to Open in Events & Approvals to accept registrations.")
        with st.form('addreg'):
            a,b=st.columns(2); name=a.text_input('Participant name'); email=b.text_input('Email'); a,b=st.columns(2); phone=a.text_input('Phone'); ref=b.text_input('Payment reference (if paid)'); amount=st.number_input('Amount submitted (₹)',min_value=0.0,value=float(event['fee']),step=50.0); submitted=st.form_submit_button('Create registration')
            if submitted:
                if not name.strip() or not email.strip(): st.error('Name and email are required.')
                elif event['registration_state']!='Open': st.error('Registrations are not open for this event.')
                elif rows('SELECT id FROM registrations WHERE event_id=? AND lower(email)=lower(?)',(evmap[selected],email)): st.error('This email is already registered for this event.')
                else:
                    pid='NX-'+date.today().strftime('%y')+'-'+''.join(secrets.choice(string.ascii_uppercase+string.digits) for _ in range(6))
                    duplicate_ref=bool(ref.strip()) and bool(rows('SELECT id FROM registrations WHERE lower(reference)=lower(?)',(ref.strip(),)))
                    if duplicate_ref: pstatus='Duplicate Reference'
                    elif amount<=0: pstatus='Unpaid'
                    elif not ref.strip(): pstatus='Missing Reference'
                    elif amount<float(event['fee']): pstatus='Partially Paid'
                    else: pstatus='Pending Verification'
                    rstatus='Payment Pending' if pstatus in ['Unpaid','Partially Paid','Missing Reference'] else 'Verification Pending'
                    run('INSERT INTO registrations(event_id,participant_id,name,email,phone,payment_amount,reference,payment_status,registration_status,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)',(evmap[selected],pid,name,email,phone,amount,ref,pstatus,rstatus,datetime.now().isoformat())); log('Created registration','Registration',f'{pid} / {name}'); st.success(f'Registration created. Participant ID: {pid}'); st.rerun()
    if t3 is not None:
        with t3:
            queue=rows("SELECT r.*,e.title event_title FROM registrations r JOIN events e ON e.id=r.event_id ORDER BY CASE r.payment_status WHEN 'Pending Verification' THEN 0 WHEN 'Duplicate Reference' THEN 1 ELSE 2 END,r.id DESC")
            for r in queue:
                with st.container(border=True):
                    a,b=st.columns([3,1]); a.markdown(f"**{r['name']}** · `{r['participant_id']}`  \n{r['event_title']} · {money(r['payment_amount'])} · Ref: {r['reference'] or 'Not provided'}  \n{badge(r['payment_status'])}",unsafe_allow_html=True)
                    if r['payment_status'] in ['Pending Verification','Duplicate Reference','Unpaid','Missing Reference','Partially Paid']:
                        with b:
                            action=st.selectbox('Review action',['Verify payment','Reject payment','Keep pending'],key=f"pa{r['id']}")
                            if st.button('Apply review',key=f"pb{r['id']}"):
                                if action=='Verify payment' and (not r['reference'] or r['payment_amount']<=0 or r['payment_status'] in ['Duplicate Reference','Partially Paid','Missing Reference','Unpaid']):
                                    st.error('Cannot verify: check the reference, duplicate flag and full fee amount first.')
                                else:
                                    status={'Verify payment':'Verified','Reject payment':'Rejected','Keep pending':'Pending Verification'}[action]; reg='Confirmed' if status=='Verified' else ('Rejected' if status=='Rejected' else 'Verification Pending')
                                    run('UPDATE registrations SET payment_status=?,registration_status=? WHERE id=?',(status,reg,r['id'])); log('Payment review','Payment',f"{r['participant_id']}: {status}"); st.success('Payment record updated.'); st.rerun()

# ---------- Committee Tasks ----------
elif page=='Committee Tasks':
    header('TEAM EXECUTION / 05','Committee responsibilities','Assign owners, set deadlines and track completion evidence for pre-event planning work.')
    STATUSES=['To Do','In Progress','Done','Blocked']
    _flash=st.session_state.pop('task_flash',None)
    if _flash: st.success(_flash)
    evmap=event_options(); _tt=make_tabs(['Task board']+(['Assign responsibility'] if role!='Principal' else [])); t1=_tt['Task board']; t2=_tt.get('Assign responsibility')
    if not evmap:
        st.info('No events yet. Create an event first, then assign committee responsibilities.')
    else:
        with t1:
            selected=st.selectbox('Event tasks',list(evmap)); tasks=rows('SELECT * FROM tasks WHERE event_id=? ORDER BY due_date',(evmap[selected],))
            if tasks:
                done=sum(x['status']=='Done' for x in tasks); st.progress(done/len(tasks),text=f'{done} of {len(tasks)} tasks complete')
                for t in tasks:
                    with st.container(border=True):
                        overdue=' · ⚠ Overdue' if (t['due_date'] or '9999')<date.today().isoformat() and t['status']!='Done' else ''
                        a,b,c=st.columns([3,1,1]); a.markdown(f"**{t['title']}**  \n{t['assignee']} · {t['team']} · Due {t['due_date']}{overdue}  \n{t['notes'] or ''}")
                        b.markdown(badge(t['priority']),unsafe_allow_html=True)
                        if role=='Principal':
                            c.markdown(badge(t['status']),unsafe_allow_html=True)
                        else:
                            cur=t['status'] if t['status'] in STATUSES else STATUSES[0]
                            current=c.selectbox('Status',STATUSES,index=STATUSES.index(cur),key=f"taskstate{t['id']}")
                            if current!=t['status'] and c.button('Update',key=f"taskupdate{t['id']}"):
                                run('UPDATE tasks SET status=? WHERE id=?',(current,t['id'])); log('Updated committee task','Task',t['title']+' → '+current); st.session_state['task_flash']='Task status updated.'; st.rerun()
            else: st.info('No tasks assigned yet.')
        if t2 is not None:
            with t2:
                selected=st.selectbox('Event for new task',list(evmap),key='taskevent')
                with st.form('newtask'):
                    title=st.text_input('Responsibility / deliverable'); a,b=st.columns(2); person=a.text_input('Assigned committee member'); team=b.selectbox('Committee',['Core Team','Marketing','Logistics','Finance','Technical','Hospitality','Speakers','Design','Other']); a,b=st.columns(2); due=a.date_input('Due date',value=date.today()+timedelta(days=7)); priority=b.selectbox('Priority',['Low','Medium','High','Critical']); notes=st.text_area('Task brief / completion criteria'); ok=st.form_submit_button('Assign task')
                    if ok:
                        if not title.strip() or not person.strip(): st.error('Task and assignee are required.')
                        else: run('INSERT INTO tasks(event_id,title,assignee,team,due_date,status,priority,notes) VALUES(?,?,?,?,?,?,?,?)',(evmap[selected],title,person,team,due.isoformat(),'To Do',priority,notes)); log('Assigned committee task','Task',title+' → '+person); st.session_state['task_flash']='Responsibility assigned.'; st.rerun()

# ---------- Finance ----------
elif page=='Finance & Sponsors':
    header('FINANCIAL CONTROL / 06','Budget, sponsorship & reconciliation','Track planned versus actual spend, payables and sponsor commitments separately from cash received.')
    evmap=event_options(); selected=st.selectbox('Event finance workspace',list(evmap)); eid=evmap[selected]
    budgets=rows('SELECT * FROM budgets WHERE event_id=?',(eid,)); sponsors=rows('SELECT * FROM sponsors WHERE event_id=?',(eid,)); event=rows('SELECT * FROM events WHERE id=?',(eid,))[0]
    planned=sum(x['planned'] for x in budgets); actual=sum(x['actual'] for x in budgets); promised=sum(x['promised'] for x in sponsors); received=sum(x['received'] for x in sponsors)
    a,b,c,d=st.columns(4); a.metric('Approved budget',money(event['budget'])); b.metric('Recorded spend',money(actual)); c.metric('Sponsor committed',money(promised)); d.metric('Sponsor received',money(received))
    _tt=make_tabs(['Expense ledger','Sponsor pipeline']+(['Add financial record'] if role in ('Faculty','HOD') else [])); t1=_tt['Expense ledger']; t2=_tt['Sponsor pipeline']; t3=_tt.get('Add financial record')
    with t1:
        if budgets: st.dataframe(pd.DataFrame(budgets),use_container_width=True,hide_index=True)
        st.metric('Budget utilisation',f'{(actual/event["budget"]*100 if event["budget"] else 0):.1f}%')
        st.metric('Planned category allocation',money(planned))
    with t2:
        if sponsors: st.dataframe(pd.DataFrame(sponsors),use_container_width=True,hide_index=True)
        st.write(f'**Outstanding cash sponsorship:** {money(max(promised-received,0))} · In-kind contributions are not included in cash received.')
    if t3 is not None:
        with t3:
            mode=st.radio('Record type',['Expense','Sponsorship'],horizontal=True)
            if mode=='Expense':
                with st.form('expense'):
                    a,b=st.columns(2); category=a.selectbox('Category',['Venue & logistics','Food & hospitality','Marketing & printing','Travel','Equipment','Prizes','Other']); payee=b.text_input('Vendor / payee'); a,b=st.columns(2); p=a.number_input('Planned amount (₹)',min_value=0.0); act=b.number_input('Actual amount (₹)',min_value=0.0); status=st.selectbox('Payment status',['Unpaid','Partially Paid','Paid','Disputed']); notes=st.text_input('Notes / receipt reference'); ok=st.form_submit_button('Add expense')
                    if ok: run('INSERT INTO budgets(event_id,category,planned,actual,payee,payment_status,notes) VALUES(?,?,?,?,?,?,?)',(eid,category,p,act,payee,status,notes)); log('Added expense','Finance',category+' / '+money(act)); st.success('Expense recorded.'); st.rerun()
            else:
                with st.form('sponsor'):
                    name=st.text_input('Sponsor name'); tier=st.selectbox('Tier',['Title','Platinum','Gold','Silver','Community','In-kind']); a,b=st.columns(2); promised2=a.number_input('Committed cash (₹)',min_value=0.0); received2=b.number_input('Cash received (₹)',min_value=0.0); status=st.selectbox('Pipeline status',['Identified','Contacted','Negotiating','Committed','Partially Received','Received','Declined','Closed']); notes=st.text_input('Agreement / proof reference'); ok=st.form_submit_button('Add sponsor')
                    if ok:
                        if not name.strip(): st.error('Sponsor name is required.')
                        else: run('INSERT INTO sponsors(event_id,name,tier,promised,received,status,notes) VALUES(?,?,?,?,?,?,?)',(eid,name,tier,promised2,received2,status,notes)); log('Added sponsor','Finance',name); st.success('Sponsor record added.'); st.rerun()
    st.markdown('### Reconciliation snapshot')
    verified_total = sum(x["payment_amount"] for x in rows("SELECT * FROM registrations WHERE event_id=? AND payment_status=?", (eid, "Verified")))
    st.write(f"Participant payment records: {money(verified_total)} verified · Sponsor cash received: {money(received)} · Recorded expense: {money(actual)}")
# ---------- Analytics ----------
elif page=='Analytics & Reports':
    header('DECISION INTELLIGENCE / 07','Analytics & reports','Descriptive metrics from the local database. No predictive performance is claimed.')
    events=rows('SELECT * FROM events'); regs=rows('SELECT * FROM registrations'); venues=rows('SELECT * FROM venues'); tasks=rows('SELECT * FROM tasks'); expenses=rows('SELECT * FROM budgets'); sponsors=rows('SELECT * FROM sponsors')
    a,b,c,d=st.columns(4); a.metric('Event portfolio',len(events)); b.metric('Participant records',len(regs)); c.metric('Committee completion',f"{(sum(x['status']=='Done' for x in tasks)/len(tasks)*100 if tasks else 0):.0f}%"); d.metric('Venue inventory',len(venues))
    left,right=st.columns(2)
    with left:
        if regs:
            df=pd.DataFrame(regs); p=df.groupby('payment_status').size().reset_index(name='Participants'); fig=px.bar(p,x='payment_status',y='Participants',title='Payment verification pipeline',color='payment_status',color_discrete_sequence=['#d6ad55','#4169e1','#6e87b8','#6d9b83']); fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font_color='#dce6fa'); st.plotly_chart(fig,use_container_width=True)
        if events:
            df=pd.DataFrame(events); counts=df.groupby('approval_state').size().reset_index(name='Events'); fig=px.pie(counts,names='approval_state',values='Events',hole=.55,title='Approval status mix',color_discrete_sequence=['#d6ad55','#4169e1','#6d9b83','#b56b7c']); fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',font_color='#dce6fa'); st.plotly_chart(fig,use_container_width=True)
    with right:
        if expenses:
            df=pd.DataFrame(expenses); g=df.groupby('category')[['planned','actual']].sum().reset_index().melt('category',var_name='Type',value_name='Amount'); fig=px.bar(g,x='category',y='Amount',color='Type',barmode='group',title='Planned vs actual expenses',color_discrete_sequence=['#4169e1','#d6ad55']); fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font_color='#dce6fa'); st.plotly_chart(fig,use_container_width=True)
        if tasks:
            df=pd.DataFrame(tasks); g=df.groupby('status').size().reset_index(name='Tasks'); fig=px.bar(g,x='status',y='Tasks',title='Committee task status',color='status',color_discrete_sequence=['#d6ad55','#4169e1','#6d9b83','#b56b7c']); fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font_color='#dce6fa'); st.plotly_chart(fig,use_container_width=True)
    st.markdown('### Venue utilisation snapshot')
    if venues:
        bdf=pd.DataFrame(venues); counts=pd.DataFrame([{'venue':v['name'],'active_bookings':sum(x['venue_id']==v['id'] and x['event_state'] not in ['Cancelled','Archived'] for x in events)} for v in venues]); fig=px.bar(counts,x='venue',y='active_bookings',title='Active event bookings by venue',color_discrete_sequence=['#d6ad55']); fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font_color='#dce6fa'); st.plotly_chart(fig,use_container_width=True)
    st.caption('Venue chart shows active booking counts, not utilisation percentage. True utilisation requires configured opening hours, maintenance windows and complete booking durations.')
    # ----- Insights & decision support -----
    st.markdown('### Insights & decision support')
    st.caption('Rule-based and descriptive: computed live from the database to show where to look and what to decide. These are not predictions.')
    if not events:
        st.info('Insights will appear once events have been created.')
    else:
        _today=date.today(); _venue={v['id']:v for v in venues}; _apps=rows('SELECT * FROM approvals')
        def _dt(sv):
            try: return datetime.strptime(str(sv)[:16],'%Y-%m-%d %H:%M')
            except Exception: return None
        _esc=_html.escape
        stats=[]
        for e in events:
            er=[r for r in regs if r['event_id']==e['id']]; et=[t for t in tasks if t['event_id']==e['id']]; eb=[b for b in expenses if b['event_id']==e['id']]
            sdt=_dt(e['start_at']); edt=_dt(e['end_at']); vv=_venue.get(e['venue_id'])
            stats.append(dict(id=e['id'],title=e['title'],club=(e['club'] or '').strip() or f"{e['department']} (no club listed)",dept=e['department'] or 'Unspecified',category=e['category'] or 'Other',start=sdt,end=edt,venue=vv['name'] if vv else '—',venue_id=e['venue_id'],cap=vv['capacity'] if vv else 0,expected=e['expected'] or 0,registered=len(er),confirmed=sum(r['registration_status']=='Confirmed' for r in er),verified=sum((r['payment_amount'] or 0) for r in er if r['payment_status']=='Verified'),budget=e['budget'] or 0,spend=sum((b['actual'] or 0) for b in eb),tasks=len(et),done=sum(t['status']=='Done' for t in et),approval=e['approval_state'],state=e['event_state'],reg_state=e['registration_state']))
        for s in stats:
            s['fill']=(s['registered']/s['expected']*100) if s['expected'] else 0
            s['days']=(s['start'].date()-_today).days if s['start'] else None
        sdf=pd.DataFrame(stats)
        def _rank(col):
            g=sdf.groupby(col).agg(Events=('id','count'),Registrations=('registered','sum'),Confirmed=('confirmed','sum'),Tasks_done=('done','sum'),Tasks=('tasks','sum'),Verified=('verified','sum')).reset_index()
            return g.sort_values(['Events','Registrations','Tasks_done'],ascending=False).reset_index(drop=True)
        cdf=_rank('club'); ddf=_rank('dept')
        def _lead(df,col,noun):
            top=df.iloc[0]; tied=df[(df.Events==top.Events)&(df.Registrations==top.Registrations)&(df.Tasks_done==top.Tasks_done)]
            detail=f"{int(top.Events)} event{'s' if top.Events!=1 else ''} · {int(top.Registrations)} registrations · {int(top.Tasks_done)} tasks done"
            if len(tied)>1: detail+=f"<br>Tied with {len(tied)-1} other {noun}{'s' if len(tied)>2 else ''}: not enough activity yet to separate them."
            return top[col],detail
        def _card(label,value,detail): return f'<div class="panel" style="min-height:128px"><div class="eyebrow">{label}</div><div style="font-size:19px;font-weight:800;color:#f2f5ff;line-height:1.25">{_esc(str(value))}</div><div class="mono" style="margin-top:7px;line-height:1.5">{detail}</div></div>'
        club_name,club_detail=_lead(cdf,'club','club'); dept_name,dept_detail=_lead(ddf,'dept','department')
        filled=sdf[sdf.registered>0].sort_values('fill',ascending=False)
        bv=pd.DataFrame([{'venue':v['name'],'n':sum(x['venue_id']==v['id'] and x['state'] not in ['Cancelled','Archived'] for x in stats)} for v in venues]).sort_values('n',ascending=False)
        k1,k2,k3,k4=st.columns(4)
        k1.markdown(_card('Most active club',club_name,club_detail),unsafe_allow_html=True)
        k2.markdown(_card('Most active department',dept_name,dept_detail),unsafe_allow_html=True)
        if len(filled): k3.markdown(_card('Best-filled event',filled.iloc[0]['title'],f"{int(filled.iloc[0]['registered'])} of {int(filled.iloc[0]['expected'])} expected registered ({filled.iloc[0]['fill']:.0f}%)"),unsafe_allow_html=True)
        else: k3.markdown(_card('Best-filled event','No registrations yet','Registrations will appear here once participants sign up.'),unsafe_allow_html=True)
        if len(bv) and bv.iloc[0]['n']>0: k4.markdown(_card('Busiest venue',bv.iloc[0]['venue'],f"{int(bv.iloc[0]['n'])} active booking{'s' if bv.iloc[0]['n']!=1 else ''}"),unsafe_allow_html=True)
        else: k4.markdown(_card('Busiest venue','No bookings yet','—'),unsafe_allow_html=True)

        st.markdown('#### Club & event analysis')
        l,r=st.columns(2)
        _lay=dict(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font_color='#dce6fa')
        with l:
            cm=cdf.rename(columns={'Tasks_done':'Tasks completed'})[['club','Events','Registrations','Tasks completed']].melt('club',var_name='Measure',value_name='Count')
            fig=px.bar(cm,x='club',y='Count',color='Measure',barmode='group',title='Club activity (events, registrations, tasks completed)',color_discrete_sequence=['#d6ad55','#4169e1','#6d9b83']); fig.update_layout(**_lay); st.plotly_chart(fig,use_container_width=True)
        with r:
            em=sdf[['title','expected','registered']].rename(columns={'expected':'Expected','registered':'Registered'}).melt('title',var_name='Measure',value_name='Participants')
            fig=px.bar(em,x='title',y='Participants',color='Measure',barmode='group',title='Registrations vs expected, by event',color_discrete_sequence=['#4169e1','#d6ad55']); fig.update_layout(**_lay); st.plotly_chart(fig,use_container_width=True)
        l,r=st.columns(2)
        with l:
            cat=sdf.groupby('category').size().reset_index(name='Events')
            fig=px.pie(cat,names='category',values='Events',hole=.55,title='Events by category',color_discrete_sequence=['#d6ad55','#4169e1','#6d9b83','#b56b7c','#6e87b8']); fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',font_color='#dce6fa'); st.plotly_chart(fig,use_container_width=True)
        with r:
            st.markdown('**Club leaderboard**')
            lb=cdf.rename(columns={'club':'Club','Tasks_done':'Tasks done','Verified':'Verified fees (₹)'})[['Club','Events','Registrations','Confirmed','Tasks done','Verified fees (₹)']]
            st.dataframe(lb,use_container_width=True,hide_index=True)
            st.caption('Ranked by number of events, then registrations, then tasks completed.')
        st.markdown('**Event performance**')
        perf=pd.DataFrame([{'Event':s['title'],'Club':s['club'],'Date':s['start'].strftime('%d %b %Y') if s['start'] else '—','Venue':s['venue'],'Expected':s['expected'],'Registered':s['registered'],'Fill %':round(s['fill']),'Confirmed':s['confirmed'],'Seat use %':round(s['expected']/s['cap']*100) if s['cap'] else None,'Verified fees (₹)':s['verified'],'Spend vs budget %':round(s['spend']/s['budget']*100) if s['budget'] else None,'Tasks done':f"{s['done']}/{s['tasks']}",'Approval':s['approval']} for s in sorted(stats,key=lambda z:(z['start'] is None,z['start']))])
        st.dataframe(perf,use_container_width=True,hide_index=True)

        # ----- Decisions to consider -----
        st.markdown('#### Decisions to consider')
        actions=[]
        def add(sev,title,detail,action): actions.append((sev,title,detail,action))
        live=[s for s in stats if s['state'] not in ('Cancelled','Archived','Completed','Financially Closed')]
        upcoming=[s for s in live if s['days'] is not None and s['days']>=0]
        for s in upcoming:
            if s['approval']!='Approved':
                pend=[a for a in _apps if a['event_id']==s['id'] and a['decision']!='Approved']; waiting=pend[0]['role'] if pend else 'the approvers'
                note={'Changes Requested':'changes were requested, so the organiser must revise and resubmit','Rejected':'it was rejected, so confirm whether to cancel or re-propose'}.get(s['approval'],f'the next decision sits with {waiting}')
                add('High' if s['days']<=14 else 'Medium',f"{s['title']} starts in {s['days']} days but is not approved",f"Approval status: {s['approval']}; {note}.",'Settle this decision soon so the venue, budget and registrations are not left hanging.')
            if s['cap'] and s['expected']>s['cap']:
                add('High',f"{s['title']} expects more people than {s['venue']} holds",f"Expected {s['expected']} vs capacity {s['cap']}.",'Move to a larger venue or cap registrations.')
            elif s['cap'] and s['expected']>0 and s['cap']>=s['expected']*2.5:
                alts=sorted([v for v in venues if v['capacity']>=s['expected']*1.1 and v['capacity']<s['cap'] and not any(o['venue_id']==v['id'] and o['id']!=s['id'] and o['start'] and o['end'] and s['start'] and s['end'] and o['start']<s['end'] and o['end']>s['start'] and o['state'] not in ('Cancelled','Archived') for o in stats)],key=lambda v:v['capacity'])
                add('Info',f"{s['title']} may be in an oversized venue",f"{s['expected']} expected in {s['venue']} (capacity {s['cap']}, about {s['expected']/s['cap']*100:.0f}% seat use).",(f"{alts[0]['name']} (capacity {alts[0]['capacity']}) is free at that time; check it has the facilities needed." if alts else 'Consider a smaller venue to free this one for larger events.'))
            if s['reg_state']=='Open' and s['expected']>0 and s['days']<=21 and s['fill']<30:
                add('Medium',f"Low registrations for {s['title']}",f"{s['registered']} of {s['expected']} expected registered ({s['fill']:.0f}%) with {s['days']} days to go.",'Promote the event, or plan for a smaller venue and budget.')
            if s['approval']=='Approved' and s['reg_state']!='Open' and s['days']<=30:
                add('Info',f"{s['title']} is approved but registration is {s['reg_state']}",f"The event is {s['days']} days away.",'Open registration if participants should be signing up now.')
            if s['tasks']>0 and s['days']<=14 and s['done']/s['tasks']<0.5:
                add('High',f"Execution risk for {s['title']}",f"Only {s['done']} of {s['tasks']} committee tasks are done with {s['days']} days to go.",'Review blocked or late tasks and reassign owners if needed.')
        overdue=[t for t in tasks if t['status']!='Done' and (t['due_date'] or '9999')<_today.isoformat()]
        if overdue: add('High',f"{len(overdue)} overdue committee task{'s' if len(overdue)!=1 else ''}",'; '.join(f"{t['title']} ({t['assignee']})" for t in overdue[:4])+('…' if len(overdue)>4 else '')+'.','Follow up with the owners or reset the deadlines.')
        pay=[r for r in regs if r['payment_status'] in ('Pending Verification','Duplicate Reference')]
        if pay: add('Medium',f"{len(pay)} payment{'s' if len(pay)!=1 else ''} awaiting review",f"{money(sum((r['payment_amount'] or 0) for r in pay))} in submitted fees is unverified; {sum(r['payment_status']=='Duplicate Reference' for r in pay)} flagged for a duplicate reference.",'Verify or reject these in Payment review so participant confirmations are not delayed.')
        for s in live:
            if s['budget'] and s['spend']>s['budget']: add('High',f"{s['title']} is over budget",f"Recorded spend {money(s['spend'])} vs approved budget {money(s['budget'])}.",'Review expenses and seek approval for the overrun.')
            elif s['budget'] and s['spend']/s['budget']>0.8: add('Medium',f"{s['title']} has used {s['spend']/s['budget']*100:.0f}% of its budget",f"{money(s['spend'])} of {money(s['budget'])} spent.",'Check remaining commitments before approving further spend.')
        over_cat=[b for b in expenses if (b['planned'] or 0)>0 and (b['actual'] or 0)>b['planned']]
        if over_cat: add('Medium',f"{len(over_cat)} expense categor{'ies' if len(over_cat)!=1 else 'y'} over plan",'; '.join(f"{b['category']} (+{money(b['actual']-b['planned'])})" for b in over_cat[:4])+'.','Re-plan or justify the extra spend.')
        out_sp=[x for x in sponsors if (x['promised'] or 0)>(x['received'] or 0)]
        if out_sp: add('Info',f"{money(sum(x['promised']-(x['received'] or 0) for x in out_sp))} of sponsor cash still outstanding",'; '.join(f"{x['name']} ({money(x['promised']-(x['received'] or 0))})" for x in out_sp[:4])+'.','Follow up on sponsor payments before committing related spend.')
        ready={}
        for a in _apps:
            if a['decision']=='Pending' and all(x['decision']=='Approved' for x in _apps if x['event_id']==a['event_id'] and x['id']<a['id']): ready[a['role']]=ready.get(a['role'],0)+1
        for role_name,n in ready.items(): add('Info',f"{n} approval decision{'s' if n!=1 else ''} ready for {role_name}",'Any earlier steps in the chain are already approved, so this one is next in line.',f'{role_name} can act now in the Approval desk.')
        for i,a1 in enumerate(live):
            for a2 in live[i+1:]:
                if a1['venue_id']==a2['venue_id'] and a1['start'] and a1['end'] and a2['start'] and a2['end'] and a1['start']<a2['end'] and a2['start']<a1['end']:
                    add('High',f"Venue clash: {a1['title']} and {a2['title']}",f"Both are booked at {a1['venue']} at overlapping times.",'Move one of the events to another venue or time.')
        idle=[v['name'] for v in venues if not any(x['venue_id']==v['id'] for x in live)]
        if idle: add('Info',f"{len(idle)} venue{'s' if len(idle)!=1 else ''} with no active bookings",', '.join(idle)+'.','Suggest these when organisers need space, to spread demand.')
        order={'High':0,'Medium':1,'Info':2}; actions.sort(key=lambda z:order[z[0]])
        if not actions: st.success('No risks flagged. Approvals, tasks, payments and budgets all look on track.')
        else:
            cnt={k:sum(1 for a in actions if a[0]==k) for k in order}
            st.markdown(''.join(f'<span class="chip">{k}: {v}</span>' for k,v in cnt.items()),unsafe_allow_html=True)
            colr={'High':('#542d38','#b56b7c'),'Medium':('#4c3c1d','#d6ad55'),'Info':('#263f70','#4169e1')}
            for sev,title,detail,action in actions:
                bg,bd=colr[sev]
                st.markdown(f'<div class="panel" style="border-left:4px solid {bd};padding:14px 18px"><span class="chip" style="background:{bg};border-color:{bd}">{sev}</span> <b>{_esc(title)}</b><div style="color:#b7c7df;margin-top:6px;font-size:14px">{_esc(detail)}</div><div class="mono" style="margin-top:6px">SUGGESTED ACTION · {_esc(action)}</div></div>',unsafe_allow_html=True)
    allrows=[]
    for table in ['events','venues','approvals','registrations','tasks','blocks','budgets','sponsors','audit']:
        for x in rows(f'SELECT * FROM {table}'): allrows.append({'table':table,**x})
    csv=pd.DataFrame(allrows).to_csv(index=False).encode('utf-8')
    st.download_button('Export consolidated data CSV',csv,file_name='nexora_data_export.csv',mime='text/csv')

# ---------- Admin ----------
elif page=='Admin & Audit':
    header('CONTROL PLANE / 08','Admin & audit','Review change history, export the local database and reset demo records.')
    logs=rows('SELECT * FROM audit ORDER BY id DESC LIMIT 100')
    if logs: st.dataframe(pd.DataFrame(logs),use_container_width=True,hide_index=True)
    else: st.info('Audit entries will appear as you use the workspace.')
    st.markdown('### Local database')
    st.code(str(DB_PATH),language='text')
    st.warning('This is a hackathon prototype. It has no authentication or production-grade role enforcement. Do not enter real student personal or financial data.')
    if DB_PATH.exists():
        st.download_button('Download SQLite database',DB_PATH.read_bytes(),file_name='nexora.db',mime='application/x-sqlite3')

st.markdown('---')
st.markdown('<div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap"><span class="mono">NEXORA · CONNECT. COORDINATE. OPTIMISE.</span><span class="mono">ROYAL BLUE / OBSIDIAN / CHAMPAGNE GOLD · PROTOTYPE BUILD</span></div>',unsafe_allow_html=True)
