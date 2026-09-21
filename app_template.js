// ---- nút Cập nhật dữ liệu (Cách 2: chuẩn bị lệnh để gửi trợ lý) ----
(function(){
  var btn=document.getElementById('btnUpdate'),box=document.getElementById('updBox'),msg=document.getElementById('updMsg'),hint=document.getElementById('updHint');
  if(!btn)return;
  btn.addEventListener('click',function(){
    box.style.display=(box.style.display==='none'||!box.style.display)?'block':'none';
    if(box.style.display==='block'&&navigator.clipboard){
      navigator.clipboard.writeText(msg.textContent).then(function(){
        hint.textContent='\u2705 \u0110\u00e3 sao ch\u00e9p c\u00e2u l\u1ec7nh. D\u00e1n v\u00e0o khung chat v\u1edbi tr\u1ee3 l\u00fd \u0111\u1ec3 nh\u1eadn d\u1eef li\u1ec7u m\u1edbi.';
      }).catch(function(){});
    }
  });
})();
const num=v=>(v==null||v==='')?0:(typeof v==='string'?parseFloat(v.replace(',','.')):v);
const T_MTCL=95.5,T_XA=94,T_MLL=41.24;
const BLUE='#1565c0',RED='#e53935',GREEN='#2e7d32',ORANGE='#fb8c00',GREY='#90a4ae';
function gline(v,t,inv){ // inv: lower is better
  return v==null?'':( (inv? v<=t : v>=t)?'ok':'bad');
}
// ---- top cards ----
const m=D.monthly;
function card(lbl,val,unit,tgt,status){
  const cls=status==='ok'?'ok':(status==='bad'?'bad':'warn');
  const stt=status==='ok'?'<span class="st ok">ĐẠT</span>':(status==='bad'?'<span class="st bad">KHÔNG ĐẠT</span>':'');
  return `<div class="card ${cls}"><div class="lbl">${lbl}</div><div class="val">${val}${unit}</div><div class="tg">${tgt}</div>${stt}</div>`;
}
document.getElementById('topcards').innerHTML=
 card('MTCL_2026 (lũy kế T9)',m.mtcl,'','Ngưỡng ≥95,5', m.mtcl>=T_MTCL?'ok':'bad')+
 card('Tỷ lệ Xã đạt MTCL',m.xa,'%','Ngưỡng ≥94%', m.xa>=T_XA?'ok':'bad')+
 card('MLL_TIME (lũy kế T9)',m.mll,' ph','Ngưỡng ≤41,24', m.mll<=T_MLL?'ok':'bad')+
 card('Số trạm quản lý',Math.round(m.sotram),'','SL Xã/Phường: '+m.sl_xa,'');
// ---- tabs ----
document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(x=>x.classList.remove('active'));
  b.classList.add('active');document.getElementById('p'+b.dataset.t).classList.add('active');
});
const labels=D.daily.map(d=>d.date);
const opt=(min,max,tgt,tlabel,inv)=>({responsive:true,maintainAspectRatio:false,plugins:{legend:{display:true,labels:{boxWidth:12,font:{size:11}}},
  annotation:{}},scales:{y:{min:min,max:max}}});
function targetDS(val,label,color){return {label:label,data:labels.map(()=>val),borderColor:color,borderDash:[6,4],pointRadius:0,borderWidth:1.5,fill:false};}
// MTCL
new Chart(cMtcl,{type:'line',data:{labels,datasets:[
 {label:'MTCL_2026',data:D.daily.map(d=>num(d.mtcl)),borderColor:BLUE,backgroundColor:'rgba(21,101,192,.12)',fill:true,tension:.3,pointRadius:3},
 targetDS(T_MTCL,'Ngưỡng 95,5',RED)]},options:opt(78,101)});
// Xa
new Chart(cXa,{type:'line',data:{labels,datasets:[
 {label:'Tỷ lệ Xã đạt (%)',data:D.daily.map(d=>num(d.xa)),borderColor:'#00897b',backgroundColor:'rgba(0,137,123,.12)',fill:true,tension:.3,pointRadius:3},
 targetDS(T_XA,'Ngưỡng 94%',RED)]},options:opt(60,100)});
// MLL
new Chart(cMll,{type:'bar',data:{labels,datasets:[
 {type:'bar',label:'MLL_TIME (ph)',data:D.daily.map(d=>num(d.mll)),backgroundColor:D.daily.map(d=>num(d.mll)<=T_MLL?'#43a047':'#e53935')},
 {type:'line',...targetDS(T_MLL,'Ngưỡng 41,24',BLUE)}]},options:opt(0,120)});
// HTMT
new Chart(cHtmt,{type:'line',data:{labels,datasets:[
 {label:'HTMT_KPI',data:D.daily.map(d=>num(d.kpi)),borderColor:BLUE,tension:.3,pointRadius:2},
 {label:'HTMT_QOS',data:D.daily.map(d=>num(d.qos)),borderColor:ORANGE,tension:.3,pointRadius:2},
 {label:'HTMT_VHKT',data:D.daily.map(d=>num(d.vhkt)),borderColor:'#8e24aa',tension:.3,pointRadius:2}]},options:opt(50,101)});
// day table
let th='<tr><th>Ngày</th><th>Tỷ lệ Xã (%)</th><th>MTCL_2026</th><th>Đánh giá</th><th>HTMT_KPI</th><th>HTMT_QOS</th><th>HTMT_VHKT</th><th>MLL_TIME</th><th>Traffic (GB)</th></tr>';
D.daily.forEach(d=>{const dat=(d.dg==='DAT');
 th+=`<tr><td>${d.date}</td><td>${d.xa}</td><td>${d.mtcl}</td><td><span class="tag ${dat?'dat':'kd'}">${dat?'ĐạT':'KHÔNG ĐẠT'}</span></td><td>${d.kpi}</td><td>${d.qos}</td><td>${d.vhkt}</td><td>${d.mll}</td><td>${Math.round(num(d.traffic)).toLocaleString('vi-VN')}</td></tr>`;});
document.getElementById('tDay').innerHTML=th;
// ---- tab2 monthly ----
document.getElementById('mmini').innerHTML=
 `<div class="c ${m.mtcl>=T_MTCL?'g':'r'}"><div class="v">${m.mtcl}</div><div class="l">MTCL_2026 (≥95,5)</div></div>`+
 `<div class="c ${m.xa>=T_XA?'g':'r'}"><div class="v">${m.xa}%</div><div class="l">Tỷ lệ Xã đạt (≥94%)</div></div>`+
 `<div class="c ${m.mll<=T_MLL?'g':'r'}"><div class="v">${m.mll}</div><div class="l">MLL_TIME phút (≤41,24)</div></div>`+
 `<div class="c o"><div class="v">${Math.round(m.sotram)}</div><div class="l">Số trạm</div></div>`;
new Chart(cRadar,{type:'radar',data:{labels:['HTMT_KPI','HTMT_QOS','HTMT_VHKT','Tỷ lệ Xã'],
 datasets:[{label:'Lũy kế T9',data:[num(m.kpi),num(m.qos),num(m.vhkt),num(m.xa)],borderColor:BLUE,backgroundColor:'rgba(21,101,192,.2)'}]},
 options:{responsive:true,maintainAspectRatio:false,scales:{r:{min:80,max:100}}}});
new Chart(cBar2,{type:'bar',data:{labels:['MTCL_2026','Tỷ lệ Xã','MLL_TIME'],datasets:[
 {label:'Thực tế',data:[num(m.mtcl),num(m.xa),num(m.mll)],backgroundColor:BLUE},
 {label:'Ngưỡng',data:[T_MTCL,T_XA,T_MLL],backgroundColor:'#ffb74d'}]},
 options:{responsive:true,maintainAspectRatio:false}});
document.getElementById('mnote').innerHTML=`<b>Nhận xét:</b> Lũy kế tháng 09/2026, MTCL_2026 đạt <b>${m.mtcl}</b> (${m.mtcl>=T_MTCL?'đạt':'dưới'} ngưỡng 95,5); Tỷ lệ Xã đạt <b>${m.xa}%</b> (${m.xa>=T_XA?'đạt':'dưới'} 94%); MLL_TIME <b>${m.mll} phút</b> (${m.mll<=T_MLL?'đạt':'vượt'} ngưỡng 41,24). Đánh giá chung: <b>${m.dg==='DAT'?'ĐẠT':'KHÔNG ĐẠT'}</b>.`;
// ---- tab3 ms ----
const s=D.ms.summary;
document.getElementById('msmini').innerHTML=
 `<div class="c"><div class="v">${s.records}</div><div class="l">Lượt mất sóng</div></div>`+
 `<div class="c o"><div class="v">${s.total_min.toLocaleString('vi-VN')}</div><div class="l">Tổng phút mất sóng</div></div>`+
 `<div class="c r"><div class="v">${s.ongoing}</div><div class="l">Đang mất LL</div></div>`+
 `<div class="c"><div class="v">${s.sites}</div><div class="l">Số trạm liên quan</div></div>`;
const L=D.ms.longest.slice(0,12).reverse();
new Chart(cLong,{type:'bar',data:{labels:L.map(x=>x.site+' ('+x.net+')'),datasets:[{label:'Phút mất LL',data:L.map(x=>x.min),
 backgroundColor:L.map(x=>x.ongoing?'#e53935':'#1565c0')}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}}}});
const F=D.ms.freq.slice(0,12).reverse();
new Chart(cFreq,{type:'bar',data:{labels:F.map(x=>x.site),datasets:[{label:'Số lần mất sóng',data:F.map(x=>x.count),backgroundColor:'#ef6c00'}]},
 options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}}}});
const ck=Object.keys(D.ms.cause),cv=Object.values(D.ms.cause);
new Chart(cCause,{type:'doughnut',data:{labels:ck,datasets:[{data:cv,backgroundColor:['#1565c0','#e53935','#fb8c00','#8e24aa','#00897b','#90a4ae']}]},
 options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'right',labels:{font:{size:11}}}}}});
const nk=Object.keys(D.ms.net),nv=Object.values(D.ms.net);
new Chart(cNet,{type:'doughnut',data:{labels:nk,datasets:[{data:nv,backgroundColor:['#1565c0','#43a047','#fb8c00','#8e24aa']}]},
 options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'right',labels:{font:{size:11}}}}}});
let ton='<tr><th class="l">Site</th><th>Lớp</th><th class="l">Khu vực</th><th>Phút mất LL</th><th class="l">Bắt đầu</th><th class="l">Nguyên nhân</th></tr>';
if(D.ms.ongoing_list.length===0) ton+='<tr><td colspan=6>Không còn trạm đang mất liên lạc</td></tr>';
D.ms.ongoing_list.forEach(x=>{ton+=`<tr><td class="l"><b>${x.site}</b></td><td>${x.net}</td><td class="l">${x.district}</td><td><span class="tag on">${x.min}</span></td><td class="l">${x.start}</td><td class="l">${x.cause||'-'}</td></tr>`;});
document.getElementById('tOn').innerHTML=ton;
let tf='<tr><th>#</th><th class="l">Site</th><th class="l">Khu vực</th><th>Lớp mạng</th><th>Số lần</th><th>Tổng phút</th><th>Dài nhất (ph)</th></tr>';
D.ms.freq.forEach((x,i)=>{tf+=`<tr><td>${i+1}</td><td class="l"><b>${x.site}</b></td><td class="l">${x.district}</td><td>${x.nets}</td><td><b>${x.count}</b></td><td>${x.total}</td><td>${x.max}</td></tr>`;});
document.getElementById('tFreq').innerHTML=tf;
