import os, re, subprocess, time
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="OS System Call Analyzer", page_icon="⚡", layout="wide")
HERE = Path(__file__).resolve().parent
SOURCE = HERE / "system_calls.c"
EXE = HERE / ("system_calls.exe" if os.name == "nt" else "system_calls")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
.stApp{background:radial-gradient(circle at 5% 5%,#c8f5ff88,transparent 25%),radial-gradient(circle at 95% 8%,#f0c9ff99,transparent 28%),linear-gradient(135deg,#f7fbff,#f5f2ff 55%,#fff7fb);color:#172554}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#10194a,#293d91 58%,#6d28d9)}
[data-testid="stSidebar"] *{color:#fff!important}
.hero{position:relative;overflow:hidden;padding:30px 34px;border-radius:26px;color:white;background:linear-gradient(115deg,#2563eb,#7c3aed 58%,#db2777);box-shadow:0 18px 45px #6554d933;animation:rise .65s ease both}
.hero h1{font-family:'Space Grotesk',sans-serif;color:white!important;font-size:clamp(30px,4vw,46px);margin:13px 0 8px}
.hero p{color:#ffffffed!important;font-size:16px;max-width:780px}
.hero .tag{display:inline-block;padding:6px 12px;border:1px solid #ffffff70;background:#ffffff24;border-radius:50px;font-size:12px;letter-spacing:1px;font-weight:700}
.hero .bolt{position:absolute;right:38px;top:28px;font-size:58px;animation:bob 2.5s ease-in-out infinite;filter:drop-shadow(0 8px 12px #0003)}
h2,h3{font-family:'Space Grotesk',sans-serif!important;color:#263578}
.section{font:700 25px 'Space Grotesk',sans-serif;color:#24336d;margin:20px 0 5px}
.sub{color:#60708b;margin-bottom:18px}
.card{background:#ffffffdf;border:1px solid #dfe7ff;border-radius:19px;padding:20px;box-shadow:0 9px 24px #1e293b0c;min-height:155px;transition:transform .2s,box-shadow .2s;animation:rise .55s ease both}
.card:hover{transform:translateY(-5px);box-shadow:0 16px 30px #6554d922}
.card h3{font-size:18px;margin:7px 0}
.card p{color:#53627e;font-size:14px;line-height:1.55;margin:0}
.pill{display:inline-block;background:#eef2ff;color:#4f46e5;border-radius:50px;padding:5px 10px;font-size:12px;font-weight:700}
.metric{background:#fff;border:1px solid #dce6ff;border-radius:18px;padding:17px;box-shadow:0 8px 24px #3341550c;animation:rise .55s ease both}
.metric .icon{font-size:24px}.metric .label{font-size:12px;font-weight:700;color:#718096;letter-spacing:.7px;text-transform:uppercase}.metric .value{font:700 29px 'Space Grotesk',sans-serif;color:#1e2b63;overflow-wrap:anywhere}.metric .hint{font-size:12px;color:#718096}
.tree{background:linear-gradient(140deg,#fff,#eff6ff);border:1px solid #dbeafe;border-radius:23px;padding:24px 14px;box-shadow:0 12px 30px #2563eb14}
.node{max-width:470px;margin:0 auto;background:white;border-radius:18px;padding:16px;text-align:center;box-shadow:0 9px 24px #1e40af18;animation:rise .65s ease both}
.parent{border:2px solid #a5b4fc}.current{border:2px solid #22d3ee;animation:rise .65s ease both,glow 2s ease-in-out infinite}
.node-title{font-weight:800;color:#253578}.node-value{color:#52617c;font-size:13px;margin-top:4px}
.arrow{text-align:center;font-size:30px;color:#6366f1;animation:arrow 1.2s ease-in-out infinite}
.callout{background:linear-gradient(110deg,#ecfeff,#eef2ff);border-left:5px solid #6366f1;border-radius:12px;padding:14px 16px;color:#334155}
div.stButton>button{border:0;border-radius:12px;color:white;font-weight:700;background:linear-gradient(100deg,#2563eb,#7c3aed 65%,#db2777);padding:.7rem 1.1rem;box-shadow:0 8px 18px #6366f13d;transition:transform .2s}
div.stButton>button:hover{color:white;transform:translateY(-2px);box-shadow:0 12px 24px #6366f155}
[data-testid="stMetric"]{background:white;padding:13px;border-radius:15px;border:1px solid #e0e7ff}
.footer{text-align:center;color:#8490a5;font-size:12px;padding:20px}
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-9px)}}
@keyframes glow{0%,100%{box-shadow:0 9px 24px #1e40af18,0 0 0 0 #06b6d433}50%{box-shadow:0 9px 24px #1e40af18,0 0 0 8px #06b6d400}}
@keyframes arrow{0%,100%{transform:translateY(0);opacity:.65}50%{transform:translateY(4px);opacity:1}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation-duration:.01ms!important;transition-duration:.01ms!important}}
</style>
""", unsafe_allow_html=True)

def compile_c():
    if not SOURCE.exists(): return False, "system_calls.c must be in the same folder as app.py."
    try:
        r = subprocess.run(["gcc", str(SOURCE), "-o", str(EXE)], capture_output=True, text=True, timeout=30)
        return (r.returncode == 0, r.stderr if r.returncode else "Compilation successful.")
    except FileNotFoundError:
        return False, "GCC not found. Install GCC; on Windows, use WSL/Linux for POSIX system calls."
    except subprocess.TimeoutExpired:
        return False, "Compilation timed out."

def run_c(choice):
    try:
        r = subprocess.run([str(EXE)], input=f"{choice}\n0\n", capture_output=True, text=True, timeout=10)
        output = r.stdout + (("\\n" + r.stderr) if r.stderr else "")
        return r.returncode == 0, output or "No output returned."
    except Exception as e:
        return False, f"Could not run the program: {e}"

def values_from(output):
    d = {"PID":"N/A", "PPID":"N/A", "UID":"N/A"}
    for k in d:
        m = re.search(rf"^{k}=(\d+)\s*$", output, re.M)
        if m: d[k] = m.group(1)
    return d

def metric(icon, label, value, hint, delay="0s"):
    st.markdown(f'<div class="metric" style="animation-delay:{delay}"><div class="icon">{icon}</div><div class="label">{label}</div><div class="value">{value}</div><div class="hint">{hint}</div></div>', unsafe_allow_html=True)

def tree(v):
    st.markdown(f"""<div class="tree">
      <div style="text-align:center;margin-bottom:15px"><span class="pill">● LIVE PROCESS RELATIONSHIP</span></div>
      <div class="node parent"><div style="font-size:25px">🧩</div><div class="node-title">Parent Process</div><div class="node-value">PPID: <b>{v['PPID']}</b></div></div>
      <div class="arrow">↓</div>
      <div class="node current"><div style="font-size:25px">⚙️</div><div class="node-title">Current Process</div><div class="node-value">PID: <b>{v['PID']}</b> &nbsp; • &nbsp; Real UID: <b>{v['UID']}</b></div></div>
    </div>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ⚡ OS LAB")
    st.caption("SYSTEM CALL ANALYZER")
    page = st.radio("NAVIGATION", ["Dashboard", "Run System Calls", "System Call Guide", "About Project"])
    st.divider()
    st.markdown("### 🧰 Tech Stack")
    st.markdown("**C** · POSIX API · **Python** · Streamlit")
    st.markdown('<div style="padding:12px;border-radius:12px;background:#ffffff20;font-size:12px">● Ready for execution</div>', unsafe_allow_html=True)

st.markdown("""<div class="hero"><div class="tag">OPERATING SYSTEMS • DIGITAL ASSIGNMENT</div><div class="bolt">⚡</div><h1>System Call Analyzer</h1><p>Explore process identity, parent–child relationships, and user identity through real C system calls — in a bright, animated dashboard.</p></div>""", unsafe_allow_html=True)

if page == "Dashboard":
    st.markdown('<div class="section">Your process command centre</div><div class="sub">A quick overview of the concepts and features in this assignment.</div>', unsafe_allow_html=True)
    a,b,c = st.columns(3)
    with a: metric("🆔","CORE SYSTEM CALLS","03","PID • PPID • UID")
    with b: metric("🧠","PROGRAM DESIGN","Modular","Functions • menu • validation",".1s")
    with c: metric("✨","VISUAL INTERFACE","Animated","Process tree • execution feedback",".2s")
    st.write("")
    st.markdown('<div class="section">Know the identifiers</div>', unsafe_allow_html=True)
    a,b,c = st.columns(3)
    with a: st.markdown('<div class="card"><span class="pill">getpid()</span><h3>🆔 PID — Process ID</h3><p>Identifies the currently running process. The value is retrieved from the C program at runtime.</p></div>',unsafe_allow_html=True)
    with b: st.markdown('<div class="card"><span class="pill">getppid()</span><h3>🌳 PPID — Parent Process ID</h3><p>Identifies the parent process and helps show the relationship between the current process and its parent.</p></div>',unsafe_allow_html=True)
    with c: st.markdown('<div class="card"><span class="pill">getuid()</span><h3>👤 UID — User ID</h3><p>Returns the real user ID associated with the process. It identifies the user, not the process.</p></div>',unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="section">Process tree preview</div>',unsafe_allow_html=True)
    tree({"PID":"retrieved on run","PPID":"retrieved on run","UID":"retrieved on run"})
    st.info("Open **Run System Calls** to compile the C program and display actual values.")

elif page == "Run System Calls":
    st.markdown('<div class="section">Run the system call demonstration</div><div class="sub">Select a report, watch the execution animation, and inspect the live identifiers.</div>',unsafe_allow_html=True)
    choices = {"View Process Information":1,"View System Call Details":2,"Analyze Parent–Child Relationship":3,"Generate Process Summary":4,"Display Complete Report":5,"Exit Program":0}
    left,right = st.columns([1.1,1])
    with left:
        st.markdown('<div class="card"><span class="pill">STEP 01</span><h3>Choose an operation</h3><p>The selected report is requested from the C program.</p></div>',unsafe_allow_html=True)
        selected = st.selectbox("Operation", list(choices.keys()))
        clicked = st.button("⚡ Compile & Run Program", type="primary", use_container_width=True)
    with right:
        st.markdown('<div class="card"><span class="pill">STEP 02</span><h3>Watch the execution</h3><p>Compilation, execution, and identifier extraction are shown with progress feedback.</p></div>',unsafe_allow_html=True)
        st.markdown('<div class="callout"><b>Animations enabled</b><br>Cards rise into view, the current-process node pulses, and the connecting arrow moves.</div>',unsafe_allow_html=True)
    if clicked:
        bar = st.progress(0, text="Preparing compilation...")
        status = st.empty()
        status.markdown("🛠️ **Compiling your C program...**")
        bar.progress(20, text="Checking source")
        time.sleep(.25)
        ok, msg = compile_c()
        if not ok:
            bar.empty(); status.empty(); st.error(msg)
        else:
            bar.progress(55, text="Compilation successful")
            status.markdown("⚙️ **Executing system calls...**")
            time.sleep(.45)
            success, output = run_c(choices[selected])
            bar.progress(85, text="Reading process identifiers")
            time.sleep(.25)
            bar.progress(100, text="Execution complete")
            time.sleep(.2)
            bar.empty(); status.empty()
            if success:
                st.success("Program executed successfully.")
                v = values_from(output)
                a,b,c = st.columns(3)
                with a: metric("🆔","PROCESS ID (PID)",v["PID"],"Returned by getpid()")
                with b: metric("🌳","PARENT PID (PPID)",v["PPID"],"Returned by getppid()",".1s")
                with c: metric("👤","REAL USER ID (UID)",v["UID"],"Returned by getuid()",".2s")
                st.write("")
                st.markdown('<div class="section">Animated process tree</div><div class="sub">Real values extracted from this execution.</div>',unsafe_allow_html=True)
                tree(v)
                st.write("")
                st.markdown('<div class="section">What do these values mean?</div>',unsafe_allow_html=True)
                t1,t2,t3 = st.tabs(["🆔 PID","🌳 PPID","👤 UID"])
                with t1: st.write("**PID — Process ID:** `getpid()` returns the identifier of the currently executing process.")
                with t2: st.write("**PPID — Parent Process ID:** `getppid()` returns the identifier of the parent. If the parent terminates, the process may be re-parented.")
                with t3: st.write("**UID — Real User ID:** `getuid()` returns the real user ID associated with the process; it is not a process identifier.")
                with st.expander("📟 Complete C terminal output",expanded=True): st.code(output,language="text")
            else:
                st.error("The program could not complete successfully.")
                st.code(output,language="text")

elif page == "System Call Guide":
    st.markdown('<div class="section">Know your system calls</div><div class="sub">Three small calls, three different pieces of information.</div>',unsafe_allow_html=True)
    with st.expander("🆔 getpid() — Current Process ID",expanded=True):
        st.write("Returns the process ID of the process that calls it.")
        st.code("pid_t pid = getpid();",language="c")
        st.markdown('<div class="callout"><b>Remember:</b> PID identifies a process, not a user.</div>',unsafe_allow_html=True)
    with st.expander("🌳 getppid() — Parent Process ID",expanded=True):
        st.write("Returns the process ID of the current process's parent.")
        st.code("pid_t ppid = getppid();",language="c")
        st.markdown('<div class="callout"><b>Remember:</b> PPID describes a process relationship.</div>',unsafe_allow_html=True)
    with st.expander("👤 getuid() — Real User ID",expanded=True):
        st.write("Returns the real user ID associated with the calling process.")
        st.code("uid_t uid = getuid();",language="c")
        st.markdown('<div class="callout"><b>Remember:</b> UID identifies the real user, not the process.</div>',unsafe_allow_html=True)
    st.warning("These functions are POSIX/Unix functions. On Windows, use WSL/Linux if your compiler does not support the required API.")

else:
    st.markdown('<div class="section">About this assignment</div><div class="sub">A practical demonstration of process-related system calls.</div>',unsafe_allow_html=True)
    a,b = st.columns(2)
    with a: st.markdown('<div class="card"><h3>🎯 Objective</h3><p>Demonstrate getpid(), getppid(), and getuid() in C and show their results in an interactive interface.</p></div>',unsafe_allow_html=True)
    with b: st.markdown('<div class="card"><h3>📌 Features</h3><p>Modular functions, menu, invalid-input handling, process relationship analysis, summary report, system-call guide, and animated process visualization.</p></div>',unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="card"><h3>🔄 Execution workflow</h3><p>C source → GCC compiler → executable → system calls → captured output → animated Streamlit dashboard.</p></div>',unsafe_allow_html=True)

st.markdown('<div class="footer">OS Digital Assignment • Process Identification & System Calls • Built with C and Streamlit</div>',unsafe_allow_html=True)
