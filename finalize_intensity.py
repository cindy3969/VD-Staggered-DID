from pathlib import Path
p=Path('scripts/add_vd_intensity.py');s=p.read_text(encoding='utf8')
s=s.replace("x=pd.read_pickle(ROOT/'deals_intensity_cache.pkl') if (ROOT/'deals_intensity_cache.pkl').exists() else pd.read_excel(SOURCE,header=1)","x=pd.read_excel(SOURCE,header=1)")
s=s.replace("with pd.io.stata.StataReader(TARGET,convert_categoricals=False) as r:","# Re-runs start from the preserved original, avoiding duplicate added columns.\nbackups=sorted(OUT.glob('original_before_intensity_*.dta'))\nBASE=backups[0] if backups else TARGET\nwith pd.io.stata.StataReader(BASE,convert_categoricals=False) as r:")
s=s.replace("backup=OUT/('original_before_intensity_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.dta')\nshutil.copy2(TARGET,backup)","backup=BASE if backups else OUT/('original_before_intensity_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.dta')\nif not backups: shutil.copy2(TARGET,backup)")
p.write_text(s,encoding='utf8')
compile(s,str(p),'exec')
import hashlib
f=Path('outputs/csdid_ultimately_granted_primary/csdid_ultimately_granted_full7316_controls.dta');o=Path('outputs/vd_intensity/csdid_ultimately_granted_full7316_controls_vd_intensity.dta')
assert hashlib.sha256(f.read_bytes()).digest()==hashlib.sha256(o.read_bytes()).digest()
with Path('outputs/vd_intensity/README.txt').open('a',encoding='utf8') as h:
 h.write('\n실제 구축 결과: 신규 28열. 최초 VD 관측 1,235 / 결측 205. 누적 사전 equity 비율 755, 직전 equity 비율 982, 후속 합계 완전 관측 1,389, 누적 VD 완전 관측 1,198. 엄격한 누락 처리 및 날짜/분류 규칙으로 첨부 표의 비율 표본 1,088과 일치하지 않음. 원 회귀 생성 코드 없이 동일 표본의 복제를 주장하지 않음.\n')
print('Final file hashes match; reproduction script syntax checked.')
