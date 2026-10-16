import numpy as np, wave
SR=44100; T=20.0; n=int(SR*T)
rng=np.random.default_rng(3)
def mtof(m): return 440*2**((m-69)/12)
def buf(): return np.zeros(n)
def place(dst, sig, t, g=1.0):
    i=int(t*SR); j=min(n,i+len(sig))
    if i<n: dst[i:j]+=sig[:j-i]*g
def env(L, a=0.005, d=0.3):
    t=np.arange(int(L*SR))/SR
    return np.minimum(1,t/a)*np.exp(-t/d)
def lp(x, a):  # one-pole lowpass
    y=np.empty_like(x); s=0.0
    for i in range(len(x)): s+=a*(x[i]-s); y[i]=s
    return y
def tone(f, L, harm=(1,), a=0.005, d=0.3):
    t=np.arange(int(L*SR))/SR
    s=sum(np.sin(2*np.pi*f*k*t)/k**1.5 for k in harm)
    return s*env(L,a,d)
def bell(f, L=1.2):
    t=np.arange(int(L*SR))/SR
    return (np.sin(2*np.pi*f*t)+0.35*np.sin(2*np.pi*f*2.01*t)*np.exp(-t/0.15)+0.15*np.sin(2*np.pi*f*3*t)*np.exp(-t/0.08))*env(L,0.002,0.35)

music, sfx, kickenv = buf(), buf(), buf()
C=[48,52,55,59]; Am=[45,48,52,55]; F=[41,45,48,52]; G=[43,47,50,55]
bars=[C,Am,F,G,C,Am,F,G,C,C]
# pad: detuned soft saws, lowpassed
pad=buf()
for b,ch in enumerate(bars):
    L=2.0 if b<9 else 2.0
    t=np.arange(int((L+0.4)*SR))/SR
    s=np.zeros_like(t)
    for m in ch:
        for det in (-0.07,0.07):
            f=mtof(m+12)*2**(det/12)
            s+=sum(np.sin(2*np.pi*f*k*t)/k for k in range(1,6))
    e=np.minimum(1,t/0.25)*np.minimum(1,np.maximum(0,(L+0.4-t)/0.4))
    if b>=8: e=np.minimum(1,t/0.05)*np.exp(-t/2.2)
    place(pad, s*e, b*2.0, 0.018)
pad=lp(pad,0.08)
# arp: 8th-note plucks of chord tones
arp=buf()
for k in range(int(16.5/0.25)):
    t0=k*0.25; ch=bars[int(t0//2)]
    m=[ch[0]+24,ch[1]+24,ch[2]+24,ch[3]+24][(k*3)%4]
    place(arp, tone(mtof(m),0.4,(1,2,3),0.003,0.12), t0, 0.06 if t0<2 else 0.075)
# bass from the drop
bass=buf()
for k in range(int((16.5-2.0)/0.25)):
    t0=2.0+k*0.25; ch=bars[int(t0//2)]
    place(bass, tone(mtof(ch[0]-12 + (12 if k%2 else 0)),0.24,(1,2),0.004,0.12), t0, 0.22)
bass=lp(bass,0.12)
# drums
def kick():
    L=0.35; t=np.arange(int(L*SR))/SR
    f=50+90*np.exp(-t/0.03); ph=2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*np.exp(-t/0.12)
def hat():
    L=0.06; x=rng.standard_normal(int(L*SR)); x=x-lp(x,0.35); return x*env(L,0.001,0.018)
def clap():
    L=0.25; x=rng.standard_normal(int(L*SR)); x=lp(x,0.5)-lp(x,0.08); return x*env(L,0.002,0.06)
drums=buf()
kbeats=[2.0+0.5*i for i in range(int((16.5-2.0)/0.5))]+[16.75]
for tk in kbeats:
    place(drums,kick(),tk,0.55); place(kickenv,np.exp(-np.arange(int(0.3*SR))/SR/0.09),tk)
for i in range(int((16.5-3.25)/0.5)): place(drums,hat(),3.25+0.5*i,0.10)
for i in range(int((16.5-8.0)/1.0)): place(drums,clap(),8.5+i*1.0,0.16)
# swell into outro
L=0.9; x=rng.standard_normal(int(L*SR)); x=lp(x,0.2); place(drums, x*np.linspace(0,1,len(x))**2, 16.75-L, 0.08)
duck=1-0.45*np.clip(kickenv,0,1)
music=(pad*1.0+bass)*duck+arp*(1-0.25*np.clip(kickenv,0,1))+drums

# sfx, all in C major pentatonic
penta=[72,74,76,79,81,84]
place(sfx, tone(mtof(67),0.3,(1,2),0.002,0.08), 1.25, 0.10)
for i,m in enumerate(penta): place(sfx, bell(mtof(m+12 if i==5 else m)), 2.0+i*0.09, 0.16)
L=0.7; x=lp(rng.standard_normal(int(L*SR)),0.06); place(sfx, x*np.sin(np.linspace(0,np.pi,len(x)))**2, 3.1, 0.25)  # whoosh
place(sfx, tone(mtof(60),0.25,(1,2,3),0.002,0.05), 4.25, 0.18)
for i,m in enumerate([76,79,84]): place(sfx, bell(mtof(m),0.8), 4.27+i*0.03, 0.05)
for k in range(34):
    L=0.03; x=rng.standard_normal(int(L*SR)); x=lp(x,0.6)-lp(x,0.15)
    place(sfx, x*env(L,0.0005,0.006), 4.8+k*0.042+rng.uniform(-0.006,0.006), 0.05*rng.uniform(0.7,1))
L=0.04; x=rng.standard_normal(int(L*SR)); place(sfx, (lp(x,0.5)-lp(x,0.1))*env(L,0.0005,0.008), 7.0, 0.22)
place(sfx, tone(mtof(52),0.12,(1,),0.001,0.03), 7.0, 0.12)
place(sfx, bell(mtof(79),0.9),7.6,0.10); place(sfx, bell(mtof(84),0.9),7.7,0.10)
for w,m in enumerate([67,69,72,74,76,79]): place(sfx, bell(mtof(m+12)), 8.7+w*0.45, 0.15)
for i,tk in enumerate([13.15,13.5,13.85]): place(sfx, tone(mtof([72,76,79][i]),0.35,(1,2),0.003,0.1), tk, 0.10)
for i,m in enumerate([72,76,79,84,88]): place(sfx, bell(mtof(m),1.8), 16.75+i*0.04, 0.09)

mix=music*0.9+sfx
# shared room: stereo convolution reverb
L=1.6; tir=np.arange(int(L*SR))/SR
out=[]
for seed in (1,2):
    ir=np.random.default_rng(seed).standard_normal(len(tir))*np.exp(-tir/0.45); ir=lp(ir,0.3); ir/=np.sqrt((ir**2).sum())
    N2=1<<int(np.ceil(np.log2(n+len(ir))))
    wet=np.fft.irfft(np.fft.rfft(mix,N2)*np.fft.rfft(ir,N2),N2)[:n]
    out.append(mix+0.22*wet)
st=np.stack(out,1)
fade=np.ones(n); k=int(1.0*SR); fade[-k:]=np.linspace(1,0,k)**1.5; st*=fade[:,None]
st=np.tanh(st*1.4)/1.4
st/=np.abs(st).max()/0.72
pcm=(st*32767).astype(np.int16)
with wave.open("audio.wav","wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("ok", st.shape)
